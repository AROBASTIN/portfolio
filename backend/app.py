import os
import re
import socket
import smtplib
import ssl
import json
import logging
import urllib.request
import urllib.error
from email.message import EmailMessage
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Load environment variables from .env file
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask application
app = Flask(__name__)

# Configure CORS
# Parse comma-separated list of allowed origins from environment (strip trailing slashes)
raw_origins = os.getenv(
    'FRONTEND_ORIGIN',
    'http://localhost:3000,http://127.0.0.1:3000,https://arobastin.is-my.id,https://arobastin.github.io'
)
allowed_origins = [origin.strip().rstrip('/') for origin in raw_origins.split(',') if origin.strip()]

CORS(
    app,
    resources={r"/api/*": {"origins": allowed_origins}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

# Initialize Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# Email regex for strict server-side validation
EMAIL_REGEX = re.compile(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+$"
)

PLACEHOLDERS = ['paste_your_gmail', 'your-app-password', 'your-email', 'example.com', 'your-api-key', 're_xxxx']


def validate_contact_payload(data):
    """
    Validates name, email, message, and honeypot field.
    Returns (is_valid, error_message, sanitized_data, is_bot)
    """
    if not isinstance(data, dict):
        return False, "Invalid request payload format.", None, False

    # Check anti-spam honeypot
    honeypot = data.get('_honeypot') or data.get('_gotcha') or ''
    if str(honeypot).strip():
        logger.warning("Spam bot detected via honeypot field.")
        return False, None, None, True

    # Validate Name
    raw_name = data.get('name')
    if not raw_name or not isinstance(raw_name, str):
        return False, "Please enter your name.", None, False
    
    name = raw_name.strip()
    if len(name) < 2 or len(name) > 100:
        return False, "Name must be between 2 and 100 characters.", None, False

    # Prevent header injection in name/subject
    if '\n' in name or '\r' in name:
        return False, "Invalid characters in name.", None, False

    # Validate Email
    raw_email = data.get('email')
    if not raw_email or not isinstance(raw_email, str):
        return False, "Please enter your email address.", None, False

    email = raw_email.strip()
    if len(email) > 254 or not EMAIL_REGEX.match(email):
        return False, "Please provide a valid email address.", None, False

    if '\n' in email or '\r' in email:
        return False, "Invalid characters in email address.", None, False

    # Validate Message
    raw_message = data.get('message')
    if not raw_message or not isinstance(raw_message, str):
        return False, "Please enter your message.", None, False

    message = raw_message.strip()
    if len(message) < 5:
        return False, "Message must be at least 5 characters long.", None, False
    if len(message) > 5000:
        return False, "Message exceeds maximum limit of 5000 characters.", None, False

    return True, None, {'name': name, 'email': email, 'message': message}, False


def send_via_resend_api(api_key: str, name: str, visitor_email: str, message_body: str, mail_to: str, mail_from: str) -> bool:
    """Sends transactional email via Resend HTTPS REST API (Port 443)."""
    try:
        logger.info("Attempting email dispatch via Resend HTTPS API...")
        
        # Resend requires onboarding@resend.dev for testing unless a verified custom domain is configured in MAIL_FROM
        mail_from_env = os.getenv('MAIL_FROM', '').strip()
        public_domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com', 'example.com', 'portfolio.local']
        if mail_from_env and not any(domain in mail_from_env.lower() for domain in public_domains):
            sender = mail_from_env
        else:
            sender = "Portfolio Contact <onboarding@resend.dev>"

        payload = {
            "from": sender,
            "to": [mail_to],
            "reply_to": visitor_email,
            "subject": f"Portfolio Contact - {name}",
            "text": f"New message from your portfolio website\n\nName:\n{name}\n\nEmail:\n{visitor_email}\n\nMessage:\n{message_body}\n"
        }
        json_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            "https://api.resend.com/emails",
            data=json_data,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "User-Agent": "PortfolioBackend/1.0"
            }
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body) if res_body else {}
            if response.status in (200, 201):
                logger.info(f"Email successfully dispatched via Resend API (ID: {res_data.get('id', 'N/A')})")
                return True
            else:
                logger.warning(f"Resend API returned HTTP {response.status}: {res_body}")
                return False
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8') if e.fp else ''
        logger.error(f"Resend API HTTPError {e.code}: {err_body}")
        return False
    except Exception as e:
        logger.error(f"Resend API dispatch failed: {str(e)}")
        return False


def send_via_brevo_api(api_key: str, name: str, visitor_email: str, message_body: str, mail_to: str, mail_from: str) -> bool:
    """Sends transactional email via Brevo (Sendinblue) HTTPS REST API (Port 443)."""
    try:
        logger.info("Attempting email dispatch via Brevo HTTPS API...")
        sender_email = mail_from if '@' in mail_from else mail_to
        payload = {
            "sender": {"name": "Portfolio Contact", "email": sender_email},
            "to": [{"email": mail_to}],
            "replyTo": {"email": visitor_email},
            "subject": f"Portfolio Contact - {name}",
            "textContent": f"New message from your portfolio website\n\nName:\n{name}\n\nEmail:\n{visitor_email}\n\nMessage:\n{message_body}\n"
        }
        json_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(
            "https://api.brevo.com/v3/smtp/email",
            data=json_data,
            method="POST",
            headers={
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "PortfolioBackend/1.0"
            }
        )
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_data = json.loads(res_body) if res_body else {}
            if response.status in (200, 201):
                logger.info(f"Email successfully dispatched via Brevo API (MessageID: {res_data.get('messageId', 'N/A')})")
                return True
            else:
                logger.warning(f"Brevo API returned HTTP {response.status}: {res_body}")
                return False
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8') if e.fp else ''
        logger.error(f"Brevo API HTTPError {e.code}: {err_body}")
        return False
    except Exception as e:
        logger.error(f"Brevo API dispatch failed: {str(e)}")
        return False


def send_via_smtp_ipv4(name: str, visitor_email: str, message_body: str, mail_host: str, mail_port: int, mail_username: str, mail_password: str, mail_from: str, mail_to: str, use_tls: bool, use_ssl: bool) -> bool:
    """
    Fallback SMTP dispatch.
    Forces IPv4 socket resolution (AF_INET) to bypass container IPv6 network unreachable errors.
    """
    safe_name = name.replace('\r', '').replace('\n', '').strip()
    msg = EmailMessage()
    msg['Subject'] = f"Portfolio Contact - {safe_name}"
    msg['From'] = mail_from
    msg['To'] = mail_to
    msg['Reply-To'] = visitor_email
    msg.set_content(
        f"New message from your portfolio website\n\n"
        f"Name:\n{safe_name}\n\n"
        f"Email:\n{visitor_email}\n\n"
        f"Message:\n{message_body}\n"
    )

    # Force IPv4 resolution to prevent [Errno 101] Network is unreachable on dual-stack hosts
    try:
        addr_info = socket.getaddrinfo(mail_host, mail_port, socket.AF_INET, socket.SOCK_STREAM)
        ipv4_target = addr_info[0][4][0]
        logger.info(f"Resolved {mail_host} to IPv4 address {ipv4_target}")
    except Exception as e:
        logger.warning(f"IPv4 resolution for {mail_host} failed ({str(e)}), falling back to hostname.")
        ipv4_target = mail_host

    ssl_context = ssl.create_default_context()
    strategies = []
    if use_ssl or mail_port == 465:
        strategies.append(('ssl', mail_port))
        strategies.append(('tls', 587))
    else:
        strategies.append(('tls', mail_port))
        strategies.append(('ssl', 465))

    last_error = None
    for mode, port in strategies:
        try:
            logger.info(f"Attempting SMTP dispatch to {mail_host} ({ipv4_target}:{port}, mode={mode})...")
            if mode == 'ssl':
                server = smtplib.SMTP_SSL(mail_host, port, context=ssl_context, timeout=8)
            else:
                server = smtplib.SMTP(mail_host, port, timeout=8)
                server.ehlo()
                if use_tls or port == 587:
                    server.starttls(context=ssl_context)
                    server.ehlo()

            server.login(mail_username, mail_password)
            server.send_message(msg)
            server.quit()
            logger.info(f"Contact email successfully sent for {safe_name} via SMTP ({mail_host}:{port})")
            return True
        except Exception as e:
            last_error = e
            logger.warning(f"SMTP attempt on {mail_host}:{port} ({mode}) failed: {str(e)}")

    logger.error(f"Failed to send email via SMTP ({mail_host}): {str(last_error)}")
    return False


def send_email_notification(name: str, visitor_email: str, message_body: str) -> bool:
    """
    Orchestrates email dispatch:
    1. Resend HTTPS API (if RESEND_API_KEY is configured)
    2. Brevo HTTPS API (if BREVO_API_KEY is configured)
    3. SMTP with forced IPv4 socket fallback
    """
    mail_to = os.getenv('MAIL_TO', 'arobastin5@gmail.com').strip()
    mail_username = os.getenv('MAIL_USERNAME', '').strip()
    mail_from = os.getenv('MAIL_FROM') or mail_username or 'arobastin5@gmail.com'
    safe_name = name.replace('\r', '').replace('\n', '').strip()

    # 1. Primary: Resend HTTPS API
    resend_key = os.getenv('RESEND_API_KEY', '').strip()
    if resend_key and not any(p in resend_key.lower() for p in PLACEHOLDERS):
        if send_via_resend_api(resend_key, safe_name, visitor_email, message_body, mail_to, mail_from):
            return True

    # 2. Secondary: Brevo HTTPS API
    brevo_key = os.getenv('BREVO_API_KEY', '').strip()
    if brevo_key and not any(p in brevo_key.lower() for p in PLACEHOLDERS):
        if send_via_brevo_api(brevo_key, safe_name, visitor_email, message_body, mail_to, mail_from):
            return True

    # 3. Tertiary: SMTP with forced IPv4
    mail_host = os.getenv('MAIL_HOST', 'smtp.gmail.com').strip()
    mail_port = int(os.getenv('MAIL_PORT', '587'))
    mail_password = os.getenv('MAIL_PASSWORD', '').replace(' ', '').strip()
    use_tls = os.getenv('MAIL_USE_TLS', 'True').lower() in ('true', '1', 'yes')
    use_ssl = os.getenv('MAIL_USE_SSL', 'False').lower() in ('true', '1', 'yes')

    if not mail_username or not mail_password or any(p in mail_username.lower() for p in PLACEHOLDERS) or any(p in mail_password.lower() for p in PLACEHOLDERS):
        logger.error("No valid email API keys (RESEND_API_KEY / BREVO_API_KEY) or SMTP credentials configured.")
        return False

    return send_via_smtp_ipv4(safe_name, visitor_email, message_body, mail_host, mail_port, mail_username, mail_password, mail_from, mail_to, use_tls, use_ssl)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for uptime monitoring and deployment status."""
    return jsonify({
        'status': 'ok',
        'service': 'Aro Bastin Portfolio Contact API',
        'version': '1.0.0'
    }), 200


@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per minute")
def handle_contact_form():
    """
    POST /api/contact
    Handles contact form submissions with validation, rate limiting, and email dispatch.
    """
    # Verify Content-Type
    if not request.is_json:
        return jsonify({
            'success': False,
            'message': 'Request content must be application/json.'
        }), 400

    data = request.get_json(silent=True)
    if data is None:
        return jsonify({
            'success': False,
            'message': 'Invalid JSON format in request.'
        }), 400

    # Validate inputs & honeypot
    is_valid, error_msg, sanitized, is_bot = validate_contact_payload(data)

    # Silent success response for bot attempts
    if is_bot:
        return jsonify({
            'success': True,
            'message': 'Message sent successfully.'
        }), 200

    if not is_valid:
        return jsonify({
            'success': False,
            'message': error_msg or 'Please provide valid name, email and message.'
        }), 400

    # Deliver email via HTTPS API or SMTP
    sent = send_email_notification(
        name=sanitized['name'],
        visitor_email=sanitized['email'],
        message_body=sanitized['message']
    )

    if not sent:
        return jsonify({
            'success': False,
            'message': 'Unable to deliver your message at this time. Please ensure backend email credentials or API keys are configured.'
        }), 500

    return jsonify({
        'success': True,
        'message': 'Thank you! Your message has been sent successfully.'
    }), 200


@app.errorhandler(429)
def ratelimit_handler(e):
    """Custom error handler for rate limit exceeded."""
    return jsonify({
        'success': False,
        'message': 'Too many requests submitted. Please wait a minute and try again.'
    }), 429


@app.errorhandler(404)
def not_found_handler(e):
    """Custom error handler for 404 routes."""
    return jsonify({
        'success': False,
        'message': 'The requested resource was not found.'
    }), 404


@app.errorhandler(500)
def internal_server_error_handler(e):
    """Custom error handler for uncaught server exceptions."""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify({
        'success': False,
        'message': 'An internal server error occurred. Please try again later.'
    }), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    logger.info(f"Starting Aro Bastin Portfolio Flask Backend on port {port} (debug={debug})...")
    app.run(host='0.0.0.0', port=port, debug=debug)

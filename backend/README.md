# Aro Bastin Portfolio — Backend Service

A secure, production-ready Python Flask backend powering the contact form on **Aro Bastin's Full Stack Developer Portfolio**.

---

## 🏗️ Architecture Overview

```
[ Visitor on Portfolio ]
       │
       │ POST https://your-backend.com/api/contact
       ▼
[ Flask Backend (backend/app.py) ]
       │
       ├─► 1. Rate Limiting (Flask-Limiter)
       ├─► 2. Anti-Spam Honeypot Verification
       ├─► 3. Server-Side Input Sanitization & Validation
       └─► 4. SMTP / Transactional Email Dispatch
       ▼
[ SMTP Server (e.g. Gmail / SendGrid / Brevo) ]
       ▼
[ arobastin5@gmail.com ] (with Visitor's Email in Reply-To)
```

---

## 🚀 Quick Start (Local Development)

### 1. Prerequisites
- Python 3.9+ installed on your system.

### 2. Navigate to the `backend/` directory
```powershell
cd backend
```

### 3. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

*(If script execution is disabled in PowerShell, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` and fill in your email credentials:
```env
FLASK_ENV=development
FLASK_DEBUG=False
PORT=5000

# Gmail SMTP Configuration
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-16-character-app-password
MAIL_FROM=your-email@gmail.com
MAIL_TO=arobastin5@gmail.com

# Allowed CORS Origins
FRONTEND_ORIGIN=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5000,https://arobastin.is-my.id
```

> [!NOTE]
> **How to create a Gmail App Password:**
> 1. Go to your [Google Account Security Settings](https://myaccount.google.com/security).
> 2. Ensure **2-Step Verification** is turned ON.
> 3. Search for **App passwords** in the search bar.
> 4. Create a new app password (name it `Portfolio Contact`).
> 5. Copy the 16-character password into `MAIL_PASSWORD` in `.env`.
> 6. *Never use your personal account password.*

### 6. Run the Flask Backend

**Development mode:**
```bash
python app.py
```
Or with Waitress (production WSGI server on Windows):
```bash
python -m waitress --port=5000 app:app
```

The backend is now live at `http://127.0.0.1:5000`.

---

## 📡 API Endpoints

### 1. Health Check
- **URL:** `GET /api/health`
- **Response:**
  ```json
  {
    "service": "Aro Bastin Portfolio Contact API",
    "status": "ok",
    "version": "1.0.0"
  }
  ```

### 2. Submit Contact Form
- **URL:** `POST /api/contact`
- **Headers:** `Content-Type: application/json`
- **Payload:**
  ```json
  {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "message": "Hi Aro, we would love to discuss a Full Stack Developer opportunity with you.",
    "_honeypot": ""
  }
  ```
- **Responses:**
  - `200 OK`:
    ```json
    {
      "success": true,
      "message": "Message sent successfully."
    }
    ```
  - `400 Bad Request`:
    ```json
    {
      "success": false,
      "message": "Please provide a valid email address."
    }
    ```
  - `429 Too Many Requests`:
    ```json
    {
      "success": false,
      "message": "Too many requests submitted. Please wait a minute and try again."
    }
    ```
  - `500 Internal Server Error`:
    ```json
    {
      "success": false,
      "message": "Unable to send your message at this time. Please try again later."
    }
    ```

---

## 🔒 Security & Best Practices

1. **Credentials Isolation:** No passwords, usernames, or secrets exist in the source code. All secrets are loaded strictly from `.env`.
2. **Git Safety:** `.env` is listed in `.gitignore`. Only `.env.example` with blank placeholders is committed.
3. **CORS Restrictions:** Only approved origins (defined in `FRONTEND_ORIGIN`) can make requests to `/api/*`.
4. **Header Injection Prevention:** Newline and CRLF characters in `name` and `email` are stripped and rejected to prevent email header manipulation.
5. **Anti-Spam Honeypot:** The frontend includes an invisible input field `_honeypot`. If filled by an automated bot, the request is safely discarded without sending email.
6. **Rate Limiting:** IP-based rate limiting prevents spam flooding (5 requests/minute).

---

## 🌐 Production Deployment Guide

Deploy your Flask backend to any cloud platform:

### Option A: Render (Recommended Free/Low-Cost)
1. Push your repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), click **New +** -> **Web Service**.
3. Connect your repository.
4. Set:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. In the **Environment Variables** tab, add:
   - `MAIL_HOST` = `smtp.gmail.com`
   - `MAIL_PORT` = `587`
   - `MAIL_USE_TLS` = `True`
   - `MAIL_USERNAME` = `your-email@gmail.com`
   - `MAIL_PASSWORD` = `your-app-password`
   - `MAIL_FROM` = `your-email@gmail.com`
   - `MAIL_TO` = `arobastin5@gmail.com`
   - `FRONTEND_ORIGIN` = `https://arobastin.is-my.id,https://arobastin.github.io`
6. Deploy the service and copy your live URL (e.g. `https://aro-portfolio-api.onrender.com`).

### Option B: Railway
1. Click **New Project** -> **Deploy from GitHub repo**.
2. Set Root Directory to `/backend`.
3. Add environment variables in the Railway dashboard.
4. Generate a public domain.

### Connecting Frontend to Production Backend
Once your backend is deployed:
1. Open `js/main.js` in your portfolio frontend.
2. Update line 12:
   ```javascript
   const API_BASE_URL = 'https://your-deployed-backend-url.com';
   ```
3. Commit and push the change to GitHub Pages.

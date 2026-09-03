# Aro Bastin — Full Stack Developer Portfolio

A premium, modern personal portfolio website for **Aro Bastin** built with semantic HTML5, Vanilla CSS3, JavaScript, and a production-ready Python Flask backend for contact form email delivery.

---

## 💻 Tech Stack

- **Frontend:** HTML5, CSS3 (Modern Dark Theme, Glassmorphism, Responsive Grid/Flexbox), Vanilla ES6+ JavaScript.
- **Backend:** Python 3, Flask, Flask-CORS, Flask-Limiter, python-dotenv, Gunicorn / Waitress.
- **Email Delivery:** SMTP (Gmail / Custom SMTP) with anti-spam honeypot, rate limiting, and visitor Reply-To routing.
- **Hosting Architecture:** 
  - Frontend: GitHub Pages / Custom Domain (`https://arobastin.is-my.id`)
  - Backend: Cloud Platform (Render, Railway, PythonAnywhere, or VPS)

---

## 📁 Project Structure

```
portfolio/
├── index.html          # Main semantic single-page layout
├── css/
│   └── styles.css      # Design system, variables, responsive styling
├── js/
│   └── main.js         # Navigation, modals, project demos, contact form integration
├── assets/             # Resume and static assets
├── backend/            # Production-ready Python Flask backend
│   ├── app.py          # Flask application with POST /api/contact
│   ├── requirements.txt# Backend dependencies
│   ├── .env.example    # Template for environment secrets
│   ├── .gitignore      # Ignores .env and venv
│   └── README.md       # Backend setup and deployment guide
├── .gitignore          # Root gitignore
└── README.md           # Project documentation
```

---

## ⚡ Running Locally

### 1. Start the Flask Backend
```powershell
cd backend
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Edit .env with your SMTP credentials
python app.py
```
Backend runs at `http://127.0.0.1:5000`.

### 2. Start the Frontend
In another terminal, in the root directory:
```powershell
npx http-server -p 3000
```
Open `http://localhost:3000` in your browser.

---

## ✉️ Contact Form API Configuration

To switch the frontend between Local Development and Production:

Open `js/main.js` and edit the single constant at the top:
```javascript
// Local Development:
const API_BASE_URL = 'http://127.0.0.1:5000';

// Production:
// const API_BASE_URL = 'https://your-backend-domain.com';
```

---

## 🔒 Security Summary
- Passwords and SMTP tokens are never stored in frontend code or committed to GitHub.
- Submissions are validated both client-side and server-side.
- Header injection prevention and spam bot honeypots are built-in.
- Rate limiting protects against automated flooding.

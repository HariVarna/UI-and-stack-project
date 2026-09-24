# AuthCore — Secure Flask Authentication System

A secure, modern, and production-ready Python Flask authentication application built with SQLite, Jinja2, Vanilla CSS, and JavaScript.

---

## 📌 Project Overview

**AuthCore** provides a complete, hardened authentication workflow featuring user registration, cryptographic password hashing, constant-time credential verification, session management, CSRF protection, and server-side route guarding.

---

## ✨ Features

* **Complete Authentication Workflow**: Registration, login, protected dashboard, and secure logout.
* **Cryptographic Security**: Password hashing powered by **Werkzeug** (`scrypt` / `pbkdf2:sha256`) with unique salts.
* **SQL Injection Protection**: 100% parameterized SQLite database queries.
* **CSRF Defense**: Global Cross-Site Request Forgery token validation on all state-changing requests via **Flask-WTF**.
* **Dual-Layer Validation**: Strict server-side and real-time client-side input validations (Name, Email RFC regex, Date of Birth boundaries, Password complexity & matching).
* **Session Hardening**: `HttpOnly` and `SameSite=Lax` cookies, configurable `Secure` flag, and session timeout.
* **Responsive UI/UX**: Custom dark-themed design system using Vanilla CSS, accessible forms, visible focus states, and password visibility toggles.
* **Automated Test Suite**: 20 comprehensive unit, integration, and security tests (`tests/test_auth.py`).

---

## 🛠️ Technology Stack

* **Backend**: Python 3, Flask 3.x
* **Security & Auth**: Werkzeug Security, Flask-WTF (CSRF)
* **Database**: SQLite 3
* **Templating**: Jinja2 (HTML5 with autoescaping)
* **Styling**: Vanilla CSS (Modern CSS variables, Glassmorphism, Responsive Grid)
* **Client-side**: Vanilla JavaScript (ES6)

---

## 📁 Project Structure

```text
UI-and-stack-project/
├── app.py                  # Main Flask application and route handlers
├── requirements.txt        # Python package dependencies
├── .env.example            # Environment configuration template
├── .gitignore              # Files and directories excluded from Git
├── README.md               # Primary project documentation
├── SECURITY.md             # Security policies and defense architecture
├── TESTING.md              # Test matrix and manual testing guide
├── database/
│   ├── schema.sql          # SQLite table definitions
│   ├── db.py               # Database connection and initialization manager
│   ├── .gitkeep            # Directory placeholder
│   └── auth.db             # Local SQLite database (generated at runtime)
├── templates/
│   ├── base.html           # Master layout with dynamic navigation and alerts
│   ├── index.html          # Public landing page with active session CTAs
│   ├── register.html       # User registration form with CSRF token
│   ├── login.html          # Sign-in form with password visibility toggle
│   └── dashboard.html      # Protected user profile overview
├── static/
│   ├── css/
│   │   └── style.css       # Design tokens, components, and responsive rules
│   └── js/
│       └── script.js       # Form validation and password visibility toggle
└── tests/
    └── test_auth.py        # Automated test suite (20 test cases)
```

---

## 🚀 Installation & Setup

### 1. Clone or Open the Repository
```powershell
cd "UI-and-stack-project"
```

### 2. Create a Python Virtual Environment
**Windows:**
```powershell
python -m venv venv
```

**macOS / Linux:**
```bash
python3 -m venv venv
```

### 3. Activate the Virtual Environment
**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables (Optional)
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

---

## 🗄️ Database Setup

Initialize the SQLite database schema:

```powershell
python database/db.py
```
*(Or run `flask --app app.py init-db`)*

This creates `database/auth.db` with the `users` table:
* `id` (`INTEGER PRIMARY KEY AUTOINCREMENT`)
* `name` (`TEXT NOT NULL`)
* `email` (`TEXT NOT NULL UNIQUE`)
* `dob` (`TEXT NOT NULL`)
* `password_hash` (`TEXT NOT NULL`)
* `created_at` (`TIMESTAMP DEFAULT CURRENT_TIMESTAMP`)

---

## ▶️ Running the Application

Start the Flask development server:
```powershell
python app.py
```

Visit the application in your browser at:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔄 Authentication Workflow

```
       [Guest]
          │
    ┌─────┴─────┐
    ▼           ▼
[Register]   [Login]
    │           │
    │ (Valid)   │ (Authenticated)
    └─────┬─────┘
          ▼
    [Dashboard] (Protected: @login_required)
          │
          ▼
       [Logout] ──> [Session Cleared] ──> [Redirect to Login]
```

1. **Register**: New users submit their Name, Email, DOB, and Password. Passwords are securely hashed, and the record is stored in SQLite.
2. **Login**: Authenticated against the stored hash. On success, an `HttpOnly` Flask session is generated.
3. **Dashboard**: Protected route requiring an active session. Displays the user's name, email, DOB, and membership timestamp. Raw passwords and hashes are never exposed.
4. **Logout**: Destroys the active session and redirects back to the login screen.

---

## 🧪 Testing

### Automated Test Suite
Run the full test suite covering all 20 authentication, session, and security test cases:
```powershell
python -m unittest tests/test_auth.py
```

### Manual Testing
Refer to [TESTING.md](file:///e:/Git%20repos/uip/UI-and-stack-project/TESTING.md) for step-by-step verification procedures.

---

## 🛡️ Security Measures

For a full breakdown of the security implementation (CSRF, XSS, SQLi, Session Security, Werkzeug hashing), see [SECURITY.md](file:///e:/Git%20repos/uip/UI-and-stack-project/SECURITY.md).

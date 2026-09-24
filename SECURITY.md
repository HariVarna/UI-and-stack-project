# Security Documentation (SECURITY.md)

This document outlines the security architecture and defensive measures implemented in the **AuthCore** Flask authentication application.

---

## 🛡️ Core Security Architecture

### 1. Cryptographic Password Security
* **One-Way Hashing**: Passwords are never stored in plaintext. They are hashed using Werkzeug's secure hashing algorithms (`scrypt` / `pbkdf2:sha256`) with automatic cryptographic salts.
* **Constant-Time Verification**: Login verification uses `werkzeug.security.check_password_hash()`, which executes comparisons in constant time to prevent timing attacks.
* **Zero Password Logging**: Passwords are never logged in console outputs, error traces, or application logs.
* **Zero Password Exposure**: Password hashes and raw passwords are never sent to the frontend or exposed in Jinja2 templates.

---

### 2. SQL Injection Defense
* **Parameterized Queries**: All database interactions use SQLite parameterized statements with `?` placeholders (e.g., `SELECT * FROM users WHERE email = ?`).
* **No String Formatting in SQL**: User inputs are never concatenated or interpolated directly into SQL queries.
* **Separation of Concerns**: Database operations are cleanly isolated in `database/db.py`.

---

### 3. Cross-Site Request Forgery (CSRF) Protection
* **Flask-WTF Integration**: CSRF protection is enabled globally across all `POST` state-changing requests using `CSRFProtect`.
* **Unique Request Tokens**: Each form embeds `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">`.
* **Safe Error Handling**: Expired or missing CSRF tokens trigger a user-friendly error without exposing server stack traces.

---

### 4. Cross-Site Scripting (XSS) Prevention
* **Autoescaping by Default**: Jinja2 autoescaping is enforced across all templates (`base.html`, `register.html`, `login.html`, `dashboard.html`).
* **Input Validation & Sanitization**: Names and email addresses are validated against strict regex patterns before any processing.

---

### 5. Session & Cookie Hardening
* **`SESSION_COOKIE_HTTPONLY = True`**: Prevents client-side scripts (JavaScript) from accessing the session cookie via `document.cookie`.
* **`SESSION_COOKIE_SAMESITE = 'Lax'`**: Prevents cross-site request forgery and cookie leakage during third-party requests.
* **`SESSION_COOKIE_SECURE`**: Configurable in production (`.env`) to ensure cookies are only transmitted over encrypted HTTPS connections.
* **Session Expiry**: Sessions expire after 2 hours of inactivity (`PERMANENT_SESSION_LIFETIME = timedelta(hours=2)`).
* **Complete Session Destruction**: The `logout` route explicitly executes `session.clear()` to invalidate authentication tokens.

---

### 6. Environment & Secret Management
* **Environment-Based Secret Key**: `SECRET_KEY` is loaded from the environment (`.env`) using `python-dotenv` with a cryptographically secure fallback (`secrets.token_hex(32)`).
* **Safe Debug Mode**: Debug mode defaults to `False` (`FLASK_DEBUG=0`) to avoid exposing interactive debuggers in production.
* **Git Hygiene**: Sensitive files (`.env`, `auth.db`, virtual environments) are excluded via `.gitignore`.

---

### 7. Server-Side Input Validation
* **Full Name**: Required, length between 2 and 50 characters, limited to alphabetic characters, spaces, hyphens, and apostrophes.
* **Email Address**: Validated with standard RFC regex, length $\le 120$ characters, duplicate accounts blocked.
* **Date of Birth**: Enforces valid `YYYY-MM-DD` calendar dates, disallows future dates, and enforces realistic birth years ($\ge 1900$).
* **Password**: Minimum 8 characters, maximum 128 characters, strict confirmation matching.
* **Generic Login Feedback**: Displays *"Invalid email or password."* for both non-existent users and wrong passwords to prevent user enumeration.

---

### 8. Graceful Error Handling
* Custom 404 and 500 error handlers prevent database error traces, stack traces, and internal server paths from ever being displayed to end users.

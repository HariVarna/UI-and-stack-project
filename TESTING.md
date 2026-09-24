# Testing Documentation (TESTING.md)

This document provides the test matrix, test procedures, automated test suite instructions, and manual test cases for the **AuthCore** application.

---

## 🧪 Automated Testing

AuthCore includes an automated test suite located in `tests/test_auth.py` covering **20 comprehensive test scenarios**.

### Running Automated Tests
Run the test suite from the project root:

```powershell
python -m unittest tests/test_auth.py
```

**Expected Output:**
```text
....................
----------------------------------------------------------------------
Ran 20 tests in ~2.5s

OK
```

---

## 📋 Comprehensive Test Matrix

### 1. Registration Test Cases

| Test ID | Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| **REG-01** | Valid Registration | Name: `Jane Doe`, Email: `jane@example.com`, DOB: `1995-05-15`, Pass: `Password123!`, Confirm: `Password123!` | Account created, password hashed in DB, redirected to `/login` with success alert. |
| **REG-02** | Empty Name | Name: `""` | Blocked with message: *"Full name is required."* |
| **REG-03** | Short Name | Name: `"J"` (< 2 chars) | Blocked with message: *"Name must be at least 2 characters long."* |
| **REG-04** | Invalid Name Chars | Name: `"Jane123@#"` | Blocked with message: *"Name can only contain letters, spaces, hyphens, and apostrophes."* |
| **REG-05** | Empty Email | Email: `""` | Blocked with message: *"Mail ID is required."* |
| **REG-06** | Invalid Email Format | Email: `jane@`, `jane.com`, `user@site..com` | Blocked with message: *"Please enter a valid email address."* |
| **REG-07** | Empty DOB | DOB: `""` | Blocked with message: *"Date of birth is required."* |
| **REG-08** | Future DOB | DOB: `2099-01-01` | Blocked with message: *"Date of birth cannot be in the future."* |
| **REG-09** | Unrealistic DOB | DOB: `1850-01-01` (< 1900) | Blocked with message: *"Please enter a realistic year of birth (after 1900)."* |
| **REG-10** | Weak Password | Password: `"pass"` (< 8 chars) | Blocked with message: *"Password must be at least 8 characters long."* |
| **REG-11** | Password Mismatch | Password: `Password123!`, Confirm: `Different123!` | Blocked with message: *"Passwords do not match."* |
| **REG-12** | Duplicate Email | Email already in SQLite database | Blocked with message: *"An account with this email already exists. Please log in."* |
| **REG-13** | Max Length Limit | Name > 50 chars or Email > 120 chars | Blocked with appropriate length error message. |

---

### 2. Login & Authentication Test Cases

| Test ID | Scenario | Input Data | Expected Result |
| :--- | :--- | :--- | :--- |
| **LOG-01** | Valid Login | Email: `jane@example.com`, Password: `Password123!` | Authenticated session created, redirected to `/dashboard` with greeting. |
| **LOG-02** | Incorrect Password | Email: `jane@example.com`, Password: `WrongPassword999` | Blocked with generic message: *"Invalid email or password."* |
| **LOG-03** | Non-existent Email | Email: `unregistered@example.com`, Password: `Password123!` | Blocked with generic message: *"Invalid email or password."* |
| **LOG-04** | Empty Fields | Email: `""`, Password: `""` | Blocked with generic message: *"Invalid email or password."* |

---

### 3. Session & Route Protection Test Cases

| Test ID | Scenario | Test Procedure | Expected Result |
| :--- | :--- | :--- | :--- |
| **SES-01** | Unauthenticated Dashboard Access | Visit `http://127.0.0.1:5000/dashboard` directly in guest browser. | Redirected to `/login` with alert: *"Please log in to access this page."* |
| **SES-02** | Authenticated Dashboard Access | Log in and visit `/dashboard`. | Displays user Name, Email, DOB, Member Since, and Logout button. |
| **SES-03** | Dashboard Refresh | Press F5 or refresh `/dashboard` while logged in. | Session persists, dashboard renders cleanly. |
| **SES-04** | Logout Action | Click **Logout** button. | Session destroyed, redirected to `/login` with message: *"You have been logged out successfully."* |
| **SES-05** | Post-Logout Access | Click browser Back button or navigate to `/dashboard` after logout. | Access denied, redirected to `/login`. |

---

### 4. Security & Database Integrity Test Cases

| Test ID | Scenario | Test Procedure | Expected Result |
| :--- | :--- | :--- | :--- |
| **SEC-01** | Password Hash Storage | Inspect `users` table via `sqlite3`. | `password_hash` contains Werkzeug hash (`scrypt:` or `pbkdf2:`); raw plaintext password is never stored. |
| **SEC-02** | No Frontend Exposure | Inspect page DOM and network response on `/dashboard`. | Password and `password_hash` are completely absent from HTML source. |
| **SEC-03** | SQL Injection Resilience | Submit `' OR '1'='1` or `admin'--` in login/register. | Neutralized by parameterized queries; treated safely as literal strings. |
| **SEC-04** | XSS Payload Resilience | Attempt submitting `<script>alert('XSS')</script>`. | Neutralized by name validation regex and Jinja2 autoescaping. |
| **SEC-05** | CSRF Protection | Submit POST request without valid `csrf_token`. | Request rejected with security error, preventing unauthorized cross-site actions. |

---

## 🧑‍💻 Manual User Journey Verification

Follow these steps to experience the complete flow as an end user:

1. **Start the server**: `python app.py`
2. **Open browser**: Navigate to `http://127.0.0.1:5000`
3. **Register**:
   - Click **Create an Account**.
   - Fill in: `Alex Hunter`, `alex.hunter@test.com`, `1992-08-14`, `HunterSecure2026!`, `HunterSecure2026!`.
   - Click the 👁️ toggle icon to verify password unmasking.
   - Click **Create Account**.
4. **Login**:
   - Enter `alex.hunter@test.com` and `HunterSecure2026!`.
   - Click **Sign In**.
5. **Dashboard**:
   - Confirm your profile information is shown.
   - Notice the dynamic navbar with your name and Logout button.
6. **Logout**:
   - Click **Logout**.
   - Confirm you are returned to the login screen.
7. **Re-Login**:
   - Log back in with the same credentials to verify session restoration.

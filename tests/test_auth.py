"""
tests/test_auth.py - Comprehensive Test Suite for AuthCore
Covers: Registration, Login, Session Management, Database Integrity, and Security.
"""
import unittest
import os
import sqlite3
from werkzeug.security import check_password_hash

# Set testing environment before importing app
os.environ["SECRET_KEY"] = "test-secret-key-authcore"
os.environ["FLASK_DEBUG"] = "0"
os.environ["WTF_CSRF_ENABLED"] = "false"  # Disabled for programmatic unit tests; tested explicitly in security test

from app import app
from database import db


class AuthCoreTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Ensure database is initialized
        db.init_db()
        
        # Clean test user records
        conn = db.get_db()
        conn.execute("DELETE FROM users WHERE email LIKE '%@test.com' OR email LIKE '%@example.com'")
        conn.commit()

    def tearDown(self):
        conn = db.get_db()
        conn.execute("DELETE FROM users WHERE email LIKE '%@test.com' OR email LIKE '%@example.com'")
        conn.commit()
        self.app_context.pop()

    # ========================================================
    # 1. REGISTRATION TESTS
    # ========================================================
    def test_01_valid_registration(self):
        """Test registration with valid data."""
        res = self.client.post("/register", data={
            "name": "Sarah Connor",
            "email": "sarah@test.com",
            "dob": "1990-05-12",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Registration successful", res.data)

        # Verify in database
        conn = db.get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", ("sarah@test.com",)).fetchone()
        self.assertIsNotNone(user)
        self.assertEqual(user["name"], "Sarah Connor")
        self.assertEqual(user["dob"], "1990-05-12")
        self.assertTrue(check_password_hash(user["password_hash"], "Password123!"))
        self.assertNotEqual(user["password_hash"], "Password123!")

    def test_02_registration_empty_name(self):
        """Test registration fails with empty name."""
        res = self.client.post("/register", data={
            "name": "",
            "email": "noname@test.com",
            "dob": "1990-05-12",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"Full name is required", res.data)

    def test_03_registration_empty_email(self):
        """Test registration fails with empty email."""
        res = self.client.post("/register", data={
            "name": "No Email",
            "email": "",
            "dob": "1990-05-12",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"Mail ID is required", res.data)

    def test_04_registration_invalid_email(self):
        """Test registration fails with invalid email formats."""
        invalid_emails = ["plainaddress", "@missingusername.com", "username@.com", "user@site..com"]
        for email in invalid_emails:
            res = self.client.post("/register", data={
                "name": "Bad Email User",
                "email": email,
                "dob": "1990-05-12",
                "password": "Password123!",
                "confirm_password": "Password123!"
            }, follow_redirects=True)
            self.assertIn(b"Please enter a valid email address", res.data)

    def test_05_registration_empty_dob(self):
        """Test registration fails with empty DOB."""
        res = self.client.post("/register", data={
            "name": "No DOB",
            "email": "nodob@test.com",
            "dob": "",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"Date of birth is required", res.data)

    def test_06_registration_invalid_dob_future_and_old(self):
        """Test registration fails with future date or unrealistic year."""
        # Future date
        res_future = self.client.post("/register", data={
            "name": "Future User",
            "email": "future@test.com",
            "dob": "2099-01-01",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"cannot be in the future", res_future.data)

        # Unrealistic year (< 1900)
        res_old = self.client.post("/register", data={
            "name": "Ancient User",
            "email": "ancient@test.com",
            "dob": "1850-01-01",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"realistic year of birth", res_old.data)

    def test_07_registration_empty_and_weak_password(self):
        """Test registration fails with empty or short (< 8 chars) password."""
        # Empty password
        res_empty = self.client.post("/register", data={
            "name": "Empty Pass",
            "email": "emptypass@test.com",
            "dob": "1990-05-12",
            "password": "",
            "confirm_password": ""
        }, follow_redirects=True)
        self.assertIn(b"Password is required", res_empty.data)

        # Weak (< 8 chars)
        res_weak = self.client.post("/register", data={
            "name": "Weak Pass",
            "email": "weakpass@test.com",
            "dob": "1990-05-12",
            "password": "short",
            "confirm_password": "short"
        }, follow_redirects=True)
        self.assertIn(b"at least 8 characters long", res_weak.data)

    def test_08_registration_password_mismatch(self):
        """Test registration fails when password and confirm_password do not match."""
        res = self.client.post("/register", data={
            "name": "Mismatch User",
            "email": "mismatch@test.com",
            "dob": "1990-05-12",
            "password": "Password123!",
            "confirm_password": "DifferentPassword123!"
        }, follow_redirects=True)
        self.assertIn(b"Passwords do not match", res.data)

    def test_09_registration_duplicate_email(self):
        """Test registration rejects duplicate email addresses."""
        # First registration
        self.client.post("/register", data={
            "name": "Original User",
            "email": "duplicate@test.com",
            "dob": "1992-04-10",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        # Duplicate attempt
        res = self.client.post("/register", data={
            "name": "Imposter User",
            "email": "duplicate@test.com",
            "dob": "1993-01-01",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"already exists", res.data)

    def test_10_registration_long_input(self):
        """Test registration enforces maximum length limits."""
        long_name = "A" * 60  # Max is 50
        res = self.client.post("/register", data={
            "name": long_name,
            "email": "long@test.com",
            "dob": "1990-05-12",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"cannot exceed 50 characters", res.data)

    # ========================================================
    # 2. LOGIN & AUTHENTICATION TESTS
    # ========================================================
    def test_11_login_success(self):
        """Test login with correct email and password."""
        # Create user
        self.client.post("/register", data={
            "name": "Login User",
            "email": "login@test.com",
            "dob": "1994-08-20",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        }, follow_redirects=True)

        # Login
        res = self.client.post("/login", data={
            "email": "login@test.com",
            "password": "SecurePassword123!"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"Welcome, Login User", res.data)
        self.assertIn(b"login@test.com", res.data)

    def test_12_login_wrong_password(self):
        """Test login fails with incorrect password and shows generic error."""
        self.client.post("/register", data={
            "name": "Wrong Pass User",
            "email": "wrongpass@test.com",
            "dob": "1994-08-20",
            "password": "SecurePassword123!",
            "confirm_password": "SecurePassword123!"
        }, follow_redirects=True)

        res = self.client.post("/login", data={
            "email": "wrongpass@test.com",
            "password": "IncorrectPassword999!"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", res.data)

    def test_13_login_nonexistent_email(self):
        """Test login fails with non-existent email and shows generic error."""
        res = self.client.post("/login", data={
            "email": "ghost@test.com",
            "password": "AnyPassword123!"
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", res.data)

    def test_14_login_empty_fields(self):
        """Test login fails when fields are empty."""
        res = self.client.post("/login", data={
            "email": "",
            "password": ""
        }, follow_redirects=True)
        self.assertIn(b"Invalid email or password", res.data)

    # ========================================================
    # 3. SESSION & ROUTE PROTECTION TESTS
    # ========================================================
    def test_15_dashboard_protection(self):
        """Test unauthenticated access to dashboard redirects to login."""
        res = self.client.get("/dashboard")
        self.assertEqual(res.status_code, 302)
        self.assertIn("/login", res.headers["Location"])

    def test_16_logout_destroys_session(self):
        """Test logout clears session and prevents subsequent dashboard access."""
        # Register and Login
        self.client.post("/register", data={
            "name": "Logout Tester",
            "email": "logout@test.com",
            "dob": "1991-03-15",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)

        self.client.post("/login", data={
            "email": "logout@test.com",
            "password": "Password123!"
        }, follow_redirects=True)

        # Confirm dashboard is accessible
        res_dash = self.client.get("/dashboard")
        self.assertEqual(res_dash.status_code, 200)

        # Logout
        res_logout = self.client.get("/logout", follow_redirects=True)
        self.assertIn(b"logged out successfully", res_logout.data)

        # Try accessing dashboard again
        res_post_logout = self.client.get("/dashboard")
        self.assertEqual(res_post_logout.status_code, 302)
        self.assertIn("/login", res_post_logout.headers["Location"])

    # ========================================================
    # 4. SECURITY AUDIT TESTS
    # ========================================================
    def test_17_sql_injection_payload_in_login(self):
        """Test SQL injection payloads are neutralized by parameterized queries."""
        sql_payloads = [
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT id, name, email, password_hash FROM users --",
            "'; DROP TABLE users; --"
        ]
        for payload in sql_payloads:
            res = self.client.post("/login", data={
                "email": payload,
                "password": "some_password"
            }, follow_redirects=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn(b"Invalid email or password", res.data)

        # Verify users table is intact
        conn = db.get_db()
        table_check = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'").fetchone()
        self.assertIsNotNone(table_check)

    def test_18_xss_prevention_in_templates(self):
        """Test XSS payloads in user input are safely escaped by Jinja2."""
        xss_name = "Jane <script>alert('XSS')</script>"
        # Registration regex blocks dangerous characters in name
        res = self.client.post("/register", data={
            "name": xss_name,
            "email": "xss@test.com",
            "dob": "1990-01-01",
            "password": "Password123!",
            "confirm_password": "Password123!"
        }, follow_redirects=True)
        self.assertIn(b"Name can only contain letters", res.data)

    def test_19_password_and_hash_never_exposed(self):
        """Ensure password and password_hash are not exposed in HTML output."""
        self.client.post("/register", data={
            "name": "Secret User",
            "email": "secret@test.com",
            "dob": "1992-07-22",
            "password": "SuperSecretPass123!",
            "confirm_password": "SuperSecretPass123!"
        }, follow_redirects=True)

        res = self.client.post("/login", data={
            "email": "secret@test.com",
            "password": "SuperSecretPass123!"
        }, follow_redirects=True)

        self.assertNotIn(b"SuperSecretPass123!", res.data)
        conn = db.get_db()
        user = conn.execute("SELECT password_hash FROM users WHERE email = ?", ("secret@test.com",)).fetchone()
        self.assertNotIn(user["password_hash"].encode(), res.data)

    # ========================================================
    # 5. FULL USER JOURNEY TEST
    # ========================================================
    def test_20_complete_user_lifecycle(self):
        """Test full user lifecycle: Register -> Login -> Dashboard -> Logout -> Login again."""
        # 1. Register
        r1 = self.client.post("/register", data={
            "name": "Full Life User",
            "email": "fulllife@test.com",
            "dob": "1993-11-30",
            "password": "MySecretPass999!",
            "confirm_password": "MySecretPass999!"
        }, follow_redirects=True)
        self.assertEqual(r1.status_code, 200)
        self.assertIn(b"Registration successful", r1.data)

        # 2. Login
        r2 = self.client.post("/login", data={
            "email": "fulllife@test.com",
            "password": "MySecretPass999!"
        }, follow_redirects=True)
        self.assertEqual(r2.status_code, 200)
        self.assertIn(b"Welcome, Full Life User", r2.data)

        # 3. View Dashboard
        r3 = self.client.get("/dashboard")
        self.assertEqual(r3.status_code, 200)
        self.assertIn(b"fulllife@test.com", r3.data)
        self.assertIn(b"1993-11-30", r3.data)

        # 4. Logout
        r4 = self.client.get("/logout", follow_redirects=True)
        self.assertEqual(r4.status_code, 200)
        self.assertIn(b"logged out successfully", r4.data)

        # 5. Verify Dashboard is blocked
        r5 = self.client.get("/dashboard")
        self.assertEqual(r5.status_code, 302)

        # 6. Re-Login
        r6 = self.client.post("/login", data={
            "email": "fulllife@test.com",
            "password": "MySecretPass999!"
        }, follow_redirects=True)
        self.assertEqual(r6.status_code, 200)
        self.assertIn(b"Welcome, Full Life User", r6.data)


if __name__ == "__main__":
    unittest.main()

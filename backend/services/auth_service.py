"""
services/auth_service.py
────────────────────────
Simple session-based authentication for the admin panel.

Security: passwords are hashed with SHA-256 + salt (stdlib only —
no extra dependencies). For a real production system, use bcrypt.
"""

import hashlib
import os
import secrets
from datetime import datetime, timedelta

from database.db_config import get_db


# ─── Helpers ───────────────────────────────────────────────────────

def _hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Return (hash, salt) for a plaintext password."""
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return hashed, salt


def _verify_password(password: str, stored_hash: str) -> bool:
    """Verify plaintext password against 'salt:hash' stored string."""
    try:
        salt, expected = stored_hash.split(":", 1)
        hashed, _ = _hash_password(password, salt)
        return hashed == expected
    except Exception:
        return False


def _make_stored_hash(password: str) -> str:
    """Return 'salt:hash' string for storage."""
    hashed, salt = _hash_password(password)
    return f"{salt}:{hashed}"


def _row_to_admin(row) -> dict:
    if not row:
        return None
    d = dict(row)
    return {
        "id":        d["id"],
        "username":  d["username"],
        "email":     d["email"],
        "createdAt": d.get("created_at", ""),
    }


# ─── Public API ────────────────────────────────────────────────────

def register_admin(username: str, email: str, password: str) -> dict:
    """
    Register a new admin account.
    Returns { success, data: admin } or { success: False, error }
    """
    username = username.strip()
    email    = email.strip().lower()

    if not username or not email or not password:
        return {"success": False, "error": "Username, email and password are required."}
    if "@" not in email:
        return {"success": False, "error": "Invalid email format."}
    if len(password) < 6:
        return {"success": False, "error": "Password must be at least 6 characters."}

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO admins (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, _make_stored_hash(password)),
        )
        db.commit()
        row = db.execute("SELECT * FROM admins WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return {"success": True, "data": _row_to_admin(row)}
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return {"success": False, "error": "An account with that email already exists."}
        return {"success": False, "error": str(exc)}


def login_admin(email: str, password: str) -> dict:
    """
    Authenticate an admin. Creates a 24-hour session token.
    Returns { success, data: { token, admin } }
    """
    email = email.strip().lower()
    db    = get_db()
    row   = db.execute("SELECT * FROM admins WHERE email = ?", (email,)).fetchone()

    if not row or not _verify_password(password, row["password_hash"]):
        return {"success": False, "error": "Invalid email or password."}

    # Create session token
    token      = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
    db.execute(
        "INSERT INTO sessions (token, admin_id, expires_at) VALUES (?, ?, ?)",
        (token, row["id"], expires_at),
    )
    db.commit()

    return {
        "success": True,
        "data": {
            "token": token,
            "admin": _row_to_admin(row),
        },
    }


def logout_admin(token: str) -> dict:
    """Invalidate a session token."""
    if not token:
        return {"success": False, "error": "No token provided."}
    db = get_db()
    db.execute("DELETE FROM sessions WHERE token = ?", (token,))
    db.commit()
    return {"success": True, "message": "Logged out."}


def get_admin_by_token(token: str) -> dict:
    """
    Validate a session token and return the admin.
    Returns { success, data: admin } or { success: False }
    """
    if not token:
        return {"success": False, "error": "No token."}
    db  = get_db()
    row = db.execute(
        """SELECT a.* FROM sessions s
           JOIN admins a ON a.id = s.admin_id
           WHERE s.token = ? AND s.expires_at > ?""",
        (token, datetime.utcnow().isoformat()),
    ).fetchone()
    if not row:
        return {"success": False, "error": "Session expired or invalid."}
    return {"success": True, "data": _row_to_admin(row)}


def ensure_default_admin() -> None:
    """
    Create a default admin account if none exist.
    Default credentials: admin@school.com / admin123
    Prints a warning to console.
    """
    db = get_db()
    count = db.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
    if count == 0:
        register_admin("Admin", "admin@school.com", "admin123")
        print("[Auth] Default admin created → email: admin@school.com  password: admin123")
        print("[Auth] CHANGE THIS PASSWORD before going to production!")

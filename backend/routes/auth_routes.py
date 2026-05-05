"""
routes/auth_routes.py
──────────────────────
Auth endpoints consumed by the GitHub frontend (login.html / signup.html).

POST /api/auth/register  — create admin account
POST /api/auth/login     — authenticate, receive token
POST /api/auth/logout    — invalidate token
GET  /api/auth/me        — validate token, get current admin
"""

from flask import Blueprint, request, jsonify
from services.auth_service import (
    register_admin,
    login_admin,
    logout_admin,
    get_admin_by_token,
)

auth_bp = Blueprint("auth", __name__)


def _get_token() -> str:
    """Extract Bearer token from Authorization header or cookie."""
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    # Fallback: token in JSON body
    body = request.get_json(silent=True) or {}
    return body.get("token", "")


@auth_bp.route("/register", methods=["POST"])
def register():
    """POST /api/auth/register  { username, email, password }"""
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "").strip()
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    result = register_admin(username, email, password)
    return jsonify(result), 201 if result["success"] else 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """POST /api/auth/login  { email, password }"""
    data     = request.get_json(silent=True) or {}
    email    = data.get("email", "").strip()
    password = data.get("password", "")

    result = login_admin(email, password)
    return jsonify(result), 200 if result["success"] else 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """POST /api/auth/logout  — invalidate current session."""
    token  = _get_token()
    result = logout_admin(token)
    return jsonify(result), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    """GET /api/auth/me — return current admin from token."""
    token  = _get_token()
    result = get_admin_by_token(token)
    return jsonify(result), 200 if result["success"] else 401

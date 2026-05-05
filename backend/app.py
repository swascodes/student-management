"""
app.py
──────
Flask application factory and entry point for the Student Manager API.

Run:
    python app.py
    # or with gunicorn (production):
    # gunicorn -w 4 "app:create_app()"
"""

import os
import sys

# Make sure intra-package imports resolve regardless of CWD
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS

from database.db_config import init_db
from routes.student_routes    import students_bp
from routes.course_routes     import courses_bp
from routes.enrollment_routes import enrollments_bp
from routes.marks_routes      import marks_bp


def create_app() -> Flask:
    """Application factory – creates and configures the Flask app."""
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), "..", "frontend"),
        static_url_path="",
    )
    app.config["JSON_SORT_KEYS"] = False   # preserve response field order

    # ── CORS ──────────────────────────────────────────────────────────
    # Allow requests from the browser's file:// origin during dev
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # ── Blueprints ────────────────────────────────────────────────────
    app.register_blueprint(students_bp,    url_prefix="/api/students")
    app.register_blueprint(courses_bp,     url_prefix="/api/courses")
    app.register_blueprint(enrollments_bp, url_prefix="/api/enrollments")
    app.register_blueprint(marks_bp,       url_prefix="/api/marks")

    # ── Database ──────────────────────────────────────────────────────
    init_db(app)

    # ── Frontend catch-all ────────────────────────────────────────────
    # Serve any HTML/CSS/JS file from the /frontend directory
    @app.route("/", defaults={"path": "index.html"})
    @app.route("/<path:path>")
    def serve_frontend(path: str):
        frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
        return send_from_directory(os.path.abspath(frontend_dir), path)

    return app


if __name__ == "__main__":
    flask_app = create_app()
    # Render (and other cloud hosts) inject the PORT env var.
    # Locally it defaults to 5000.
    port      = int(os.environ.get("PORT", 5000))
    debug     = os.environ.get("FLASK_ENV") != "production"
    print(f"\n[Student Manager] API running at http://0.0.0.0:{port}\n")
    flask_app.run(debug=debug, port=port, host="0.0.0.0")

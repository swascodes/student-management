"""
routes/marks_routes.py
──────────────────────
Endpoints for adding/updating marks and fetching academic summaries.

Base path: /api/marks
"""

from flask import Blueprint, request, jsonify
from services.marks_service import (
    add_or_update_marks,
    get_student_marks,
    calculate_average,
)

marks_bp = Blueprint("marks", __name__)


@marks_bp.route("", methods=["POST"])
def save_marks():
    """
    POST /api/marks
    Body: { student_id, course_id, marks }
    Upserts marks for the given student/course pair.
    """
    data       = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    course_id  = data.get("course_id")
    marks      = data.get("marks")

    if student_id is None or course_id is None or marks is None:
        return jsonify({"success": False, "error": "student_id, course_id, and marks are required."}), 400

    result = add_or_update_marks(int(student_id), int(course_id), marks)
    return jsonify(result), 200 if result["success"] else 400


@marks_bp.route("/<int:student_id>", methods=["GET"])
def student_marks(student_id: int):
    """
    GET /api/marks/<student_id>
    Returns all marks for the student with total, average, and grade.
    """
    result = get_student_marks(student_id)
    return jsonify(result), 200 if result["success"] else 404


@marks_bp.route("/<int:student_id>/summary", methods=["GET"])
def marks_summary(student_id: int):
    """GET /api/marks/<student_id>/summary – Return just average + grade."""
    result = calculate_average(student_id)
    return jsonify(result), 200 if result["success"] else 404

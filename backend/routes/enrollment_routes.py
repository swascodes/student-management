"""
routes/enrollment_routes.py
───────────────────────────
Endpoints for managing student ↔ course enrollments.

Base path: /api/enrollments
"""

from flask import Blueprint, request, jsonify
from services.enrollment_service import (
    enroll_student,
    get_student_courses,
    remove_enrollment,
    get_students_by_course,
)

enrollments_bp = Blueprint("enrollments", __name__)


@enrollments_bp.route("", methods=["POST"])
def enroll():
    """
    POST /api/enrollments
    Body: { student_id, course_id }
    """
    data       = request.get_json(silent=True) or {}
    student_id = data.get("student_id")
    course_id  = data.get("course_id")

    if not student_id or not course_id:
        return jsonify({"success": False, "error": "student_id and course_id are required."}), 400

    result = enroll_student(int(student_id), int(course_id))
    return jsonify(result), 201 if result["success"] else 400


@enrollments_bp.route("/student/<int:student_id>", methods=["GET"])
def student_courses(student_id: int):
    """GET /api/enrollments/student/<id> – List all courses for a student."""
    result = get_student_courses(student_id)
    return jsonify(result), 200 if result["success"] else 404


@enrollments_bp.route("/course/<int:course_id>", methods=["GET"])
def course_students(course_id: int):
    """GET /api/enrollments/course/<id> – List all students in a course."""
    result = get_students_by_course(course_id)
    return jsonify(result), 200 if result["success"] else 404


@enrollments_bp.route("/<int:student_id>/<int:course_id>", methods=["DELETE"])
def unenroll(student_id: int, course_id: int):
    """DELETE /api/enrollments/<student_id>/<course_id> – Remove enrollment."""
    result = remove_enrollment(student_id, course_id)
    return jsonify(result), 200 if result["success"] else 404

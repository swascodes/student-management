"""
routes/student_routes.py
────────────────────────
RESTful endpoints for student CRUD operations.

Base path: /api/students
"""

from flask import Blueprint, request, jsonify
from services.student_service import (
    create_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
)

students_bp = Blueprint("students", __name__)


@students_bp.route("", methods=["GET"])
def list_students():
    """
    GET /api/students
    Optional query param: ?search=<term>
    Returns all students, filtered by name/ID if search is provided.
    """
    search = request.args.get("search", "").strip()
    result = get_all_students(search)
    return jsonify(result), 200


@students_bp.route("", methods=["POST"])
def add_student():
    """POST /api/students – Create a new student."""
    data   = request.get_json(silent=True) or {}
    result = create_student(data)
    status = 201 if result["success"] else 400
    return jsonify(result), status


@students_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id: int):
    """GET /api/students/<id> – Fetch a student by ID."""
    result = get_student_by_id(student_id)
    status = 200 if result["success"] else 404
    return jsonify(result), status


@students_bp.route("/<int:student_id>", methods=["PUT"])
def edit_student(student_id: int):
    """PUT /api/students/<id> – Update student fields."""
    data   = request.get_json(silent=True) or {}
    result = update_student(student_id, data)
    status = 200 if result["success"] else 400
    return jsonify(result), status


@students_bp.route("/<int:student_id>", methods=["DELETE"])
def remove_student(student_id: int):
    """DELETE /api/students/<id> – Delete a student (cascades)."""
    result = delete_student(student_id)
    status = 200 if result["success"] else 404
    return jsonify(result), status

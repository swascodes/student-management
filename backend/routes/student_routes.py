"""
routes/student_routes.py  (v2)
──────────────────────────────
RESTful endpoints with extended query params and /stats route.
Base path: /api/students
"""

from flask import Blueprint, request, jsonify
from services.student_service import (
    create_student,
    get_all_students,
    get_student_by_id,
    update_student,
    delete_student,
    get_stats,
)

students_bp = Blueprint("students", __name__)


@students_bp.route("/stats", methods=["GET"])
def stats():
    """GET /api/students/stats — dashboard statistics."""
    return jsonify(get_stats()), 200


@students_bp.route("", methods=["GET"])
def list_students():
    """
    GET /api/students
    Query params: search, department, grade, sortBy, sortDir, page, pageSize
    """
    result = get_all_students(
        search     = request.args.get("search", "").strip(),
        department = request.args.get("department", "").strip(),
        grade      = request.args.get("grade", "").strip(),
        sort_by    = request.args.get("sortBy", "created_at"),
        sort_dir   = request.args.get("sortDir", "desc"),
        page       = int(request.args.get("page", 0) or 0),
        page_size  = int(request.args.get("pageSize", 0) or 0),
    )
    return jsonify(result), 200


@students_bp.route("", methods=["POST"])
def add_student():
    """POST /api/students — create student with extended fields."""
    data   = request.get_json(silent=True) or {}
    result = create_student(data)
    return jsonify(result), 201 if result["success"] else 400


@students_bp.route("/<int:student_id>", methods=["GET"])
def get_student(student_id: int):
    """GET /api/students/<id>"""
    result = get_student_by_id(student_id)
    return jsonify(result), 200 if result["success"] else 404


@students_bp.route("/<int:student_id>", methods=["PUT"])
def edit_student(student_id: int):
    """PUT /api/students/<id>"""
    data   = request.get_json(silent=True) or {}
    result = update_student(student_id, data)
    return jsonify(result), 200 if result["success"] else 400


@students_bp.route("/<int:student_id>", methods=["DELETE"])
def remove_student(student_id: int):
    """DELETE /api/students/<id>"""
    result = delete_student(student_id)
    return jsonify(result), 200 if result["success"] else 404

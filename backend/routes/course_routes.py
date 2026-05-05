"""
routes/course_routes.py
───────────────────────
RESTful endpoints for course CRUD operations.

Base path: /api/courses
"""

from flask import Blueprint, request, jsonify
from services.course_service import (
    create_course,
    get_all_courses,
    get_course_by_id,
    update_course,
    delete_course,
)

courses_bp = Blueprint("courses", __name__)


@courses_bp.route("", methods=["GET"])
def list_courses():
    """GET /api/courses – Return all courses."""
    return jsonify(get_all_courses()), 200


@courses_bp.route("", methods=["POST"])
def add_course():
    """POST /api/courses – Create a new course."""
    data   = request.get_json(silent=True) or {}
    result = create_course(data)
    return jsonify(result), 201 if result["success"] else 400


@courses_bp.route("/<int:course_id>", methods=["GET"])
def get_course(course_id: int):
    """GET /api/courses/<id> – Get a course by ID."""
    result = get_course_by_id(course_id)
    return jsonify(result), 200 if result["success"] else 404


@courses_bp.route("/<int:course_id>", methods=["PUT"])
def edit_course(course_id: int):
    """PUT /api/courses/<id> – Update course fields."""
    data   = request.get_json(silent=True) or {}
    result = update_course(course_id, data)
    return jsonify(result), 200 if result["success"] else 400


@courses_bp.route("/<int:course_id>", methods=["DELETE"])
def remove_course(course_id: int):
    """DELETE /api/courses/<id> – Delete a course (cascades)."""
    result = delete_course(course_id)
    return jsonify(result), 200 if result["success"] else 404

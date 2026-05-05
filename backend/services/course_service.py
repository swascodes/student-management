"""
services/course_service.py
──────────────────────────
Business logic for course CRUD operations.
"""

from database.db_config import get_db


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def _validate_course_data(data: dict, require_all: bool = True) -> list[str]:
    errors = []
    if require_all or "course_name" in data:
        if not data.get("course_name", "").strip():
            errors.append("Course name is required.")
    if require_all or "credits" in data:
        try:
            credits = int(data.get("credits", 0))
            if credits <= 0:
                errors.append("Credits must be a positive integer.")
        except (ValueError, TypeError):
            errors.append("Credits must be a valid integer.")
    if require_all or "instructor_name" in data:
        if not data.get("instructor_name", "").strip():
            errors.append("Instructor name is required.")
    return errors


def create_course(data: dict) -> dict:
    """Insert a new course record."""
    errors = _validate_course_data(data)
    if errors:
        return {"success": False, "error": "; ".join(errors)}

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO courses (course_name, credits, instructor_name) VALUES (?, ?, ?)",
            (
                data["course_name"].strip(),
                int(data["credits"]),
                data["instructor_name"].strip(),
            ),
        )
        db.commit()
        row = db.execute("SELECT * FROM courses WHERE id = ?", (cursor.lastrowid,)).fetchone()
        return {"success": True, "course": _row_to_dict(row)}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_all_courses() -> dict:
    """Return all courses ordered by name."""
    db   = get_db()
    rows = db.execute("SELECT * FROM courses ORDER BY course_name").fetchall()
    return {"success": True, "courses": [_row_to_dict(r) for r in rows]}


def get_course_by_id(course_id: int) -> dict:
    db  = get_db()
    row = db.execute("SELECT * FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not row:
        return {"success": False, "error": f"Course {course_id} not found."}
    return {"success": True, "course": _row_to_dict(row)}


def update_course(course_id: int, data: dict) -> dict:
    """Partially update a course record."""
    check = get_course_by_id(course_id)
    if not check["success"]:
        return check

    errors = _validate_course_data(data, require_all=False)
    if errors:
        return {"success": False, "error": "; ".join(errors)}

    db = get_db()
    try:
        credits = int(data["credits"]) if "credits" in data else None
        db.execute(
            """UPDATE courses
               SET course_name     = COALESCE(?, course_name),
                   credits         = COALESCE(?, credits),
                   instructor_name = COALESCE(?, instructor_name)
               WHERE id = ?""",
            (
                data.get("course_name", "").strip() or None,
                credits,
                data.get("instructor_name", "").strip() or None,
                course_id,
            ),
        )
        db.commit()
        return {"success": True, "course": get_course_by_id(course_id)["course"]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def delete_course(course_id: int) -> dict:
    """Delete a course (cascades to enrollments + marks)."""
    check = get_course_by_id(course_id)
    if not check["success"]:
        return check

    db = get_db()
    db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
    db.commit()
    return {"success": True, "message": f"Course {course_id} deleted."}

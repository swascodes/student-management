"""
services/student_service.py
───────────────────────────
Business logic for student CRUD operations.

All functions receive/return plain Python dicts so the route layer
stays thin and testable.
"""

from database.db_config import get_db


# ────────────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────────────

def _row_to_dict(row) -> dict:
    """Convert a sqlite3.Row to a plain dict."""
    return dict(row) if row else None


def _validate_student_data(data: dict, require_all: bool = True) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors = []
    name  = data.get("name", "").strip()
    email = data.get("email", "").strip()
    phone = data.get("phone", "").strip()

    if require_all or "name" in data:
        if not name:
            errors.append("Name is required.")
    if require_all or "email" in data:
        if not email:
            errors.append("Email is required.")
        elif "@" not in email:
            errors.append("Invalid email format.")
    # Phone is optional — but if provided it must be exactly 10 digits
    if phone:
        if not phone.isdigit():
            errors.append("Phone number must contain digits only.")
        elif len(phone) != 10:
            errors.append("Phone number must be exactly 10 digits.")
    return errors



# ────────────────────────────────────────────────────────────────────
# CRUD
# ────────────────────────────────────────────────────────────────────

def create_student(data: dict) -> dict:
    """
    Insert a new student record.

    Returns:
        dict with keys: success (bool), student (dict) | error (str)
    """
    errors = _validate_student_data(data)
    if errors:
        return {"success": False, "error": "; ".join(errors)}

    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO students (name, email, phone, dob, address)
               VALUES (?, ?, ?, ?, ?)""",
            (
                data["name"].strip(),
                data["email"].strip().lower(),
                data.get("phone", "").strip() or None,
                data.get("dob") or None,
                data.get("address", "").strip() or None,
            ),
        )
        db.commit()
        new_id = cursor.lastrowid
        return {"success": True, "student": get_student_by_id(new_id)["student"]}
    except db.IntegrityError:
        return {"success": False, "error": "A student with that email already exists."}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_all_students(search: str = "") -> dict:
    """
    Fetch all students, optionally filtered by name or ID.

    Args:
        search: Free-text filter applied to name and id columns.
    """
    db = get_db()
    if search:
        pattern = f"%{search}%"
        rows = db.execute(
            "SELECT * FROM students WHERE name LIKE ? OR CAST(id AS TEXT) LIKE ? ORDER BY name",
            (pattern, pattern),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM students ORDER BY name").fetchall()

    return {"success": True, "students": [_row_to_dict(r) for r in rows]}


def get_student_by_id(student_id: int) -> dict:
    """Fetch a single student by primary key."""
    db  = get_db()
    row = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not row:
        return {"success": False, "error": f"Student {student_id} not found."}
    return {"success": True, "student": _row_to_dict(row)}


def update_student(student_id: int, data: dict) -> dict:
    """Partially or fully update a student record."""
    # First confirm student exists
    check = get_student_by_id(student_id)
    if not check["success"]:
        return check

    errors = _validate_student_data(data, require_all=False)
    if errors:
        return {"success": False, "error": "; ".join(errors)}

    db = get_db()
    try:
        db.execute(
            """UPDATE students
               SET name    = COALESCE(?, name),
                   email   = COALESCE(?, email),
                   phone   = COALESCE(?, phone),
                   dob     = COALESCE(?, dob),
                   address = COALESCE(?, address)
               WHERE id = ?""",
            (
                data.get("name", "").strip() or None,
                data.get("email", "").strip().lower() or None,
                data.get("phone", "").strip() or None,
                data.get("dob") or None,
                data.get("address", "").strip() or None,
                student_id,
            ),
        )
        db.commit()
        return {"success": True, "student": get_student_by_id(student_id)["student"]}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def delete_student(student_id: int) -> dict:
    """Delete a student and cascade-remove their enrollments and marks."""
    check = get_student_by_id(student_id)
    if not check["success"]:
        return check

    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    return {"success": True, "message": f"Student {student_id} deleted."}

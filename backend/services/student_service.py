"""
services/student_service.py  (v2)
──────────────────────────────────
Extended CRUD with:
  - rollNo, department, marks, grade, bloodGroup, guardian fields
  - Response shape normalised to { success, data } matching the
    GitHub frontend's api.js expectations
  - Stats endpoint
  - Department / grade filtering + sorting
"""

import re
from database.db_config import get_db


# ────────────────────────────────────────────────────────────────────
# Grade helper (mirrors frontend _grade())
# ────────────────────────────────────────────────────────────────────

def _assign_grade(marks) -> str:
    """Assign letter grade from numeric marks."""
    if marks is None:
        return ""
    m = float(marks)
    if m >= 90: return "A+"
    if m >= 80: return "A"
    if m >= 70: return "B+"
    if m >= 60: return "B"
    if m >= 50: return "C"
    if m >= 40: return "D"
    return "F"


# ────────────────────────────────────────────────────────────────────
# Row → dict normaliser
# ────────────────────────────────────────────────────────────────────

def _row_to_student(row) -> dict:
    """Convert a sqlite3.Row to the student dict the frontend expects."""
    if not row:
        return None
    d = dict(row)
    # Rename snake_case DB columns to camelCase for the frontend
    return {
        "id":               d["id"],
        "name":             d["name"],
        "email":            d["email"],
        "phone":            d.get("phone") or "",
        "dob":              d.get("dob") or "",
        "address":          d.get("address") or "",
        "rollNo":           d.get("roll_no") or "",
        "department":       d.get("department") or "",
        "marks":            d.get("marks"),
        "grade":            d.get("grade") or "",
        "bloodGroup":       d.get("blood_group") or "",
        "guardianName":     d.get("guardian_name") or "",
        "guardianContact":  d.get("guardian_contact") or "",
        "joinDate":         d.get("join_date") or "",
        "createdAt":        d.get("created_at") or "",
        "updatedAt":        d.get("updated_at") or "",
    }


# ────────────────────────────────────────────────────────────────────
# Validation
# ────────────────────────────────────────────────────────────────────

def _validate(data: dict, require_all: bool = True) -> list[str]:
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
    # Phone: optional but must be 10 digits if provided
    if phone:
        if not phone.isdigit():
            errors.append("Phone number must contain digits only.")
        elif len(phone) != 10:
            errors.append("Phone number must be exactly 10 digits.")
    # Marks: optional but 0–100 if provided
    marks = data.get("marks")
    if marks is not None and marks != "":
        try:
            m = float(marks)
            if not (0 <= m <= 100):
                errors.append("Marks must be between 0 and 100.")
        except (ValueError, TypeError):
            errors.append("Marks must be a valid number.")
    return errors


# ────────────────────────────────────────────────────────────────────
# CRUD
# ────────────────────────────────────────────────────────────────────

def create_student(data: dict) -> dict:
    """Insert a new student.  Returns { success, data: student }."""
    errors = _validate(data)
    if errors:
        return {"success": False, "error": "; ".join(errors)}

    marks = float(data["marks"]) if data.get("marks") not in (None, "") else None
    grade = _assign_grade(marks) if marks is not None else ""

    db = get_db()
    try:
        cursor = db.execute(
            """INSERT INTO students
               (name, email, phone, dob, address,
                roll_no, department, marks, grade,
                blood_group, guardian_name, guardian_contact, join_date)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                data["name"].strip(),
                data["email"].strip().lower(),
                data.get("phone", "").strip() or None,
                data.get("dob") or None,
                data.get("address", "").strip() or None,
                data.get("rollNo", "").strip() or None,
                data.get("department", "").strip() or None,
                marks,
                grade or None,
                data.get("bloodGroup", "").strip() or None,
                data.get("guardianName", "").strip() or None,
                data.get("guardianContact", "").strip() or None,
                data.get("joinDate") or None,
            ),
        )
        db.commit()
        return {"success": True, "data": get_student_by_id(cursor.lastrowid)["data"]}
    except Exception as exc:
        msg = str(exc)
        if "UNIQUE" in msg and "email" in msg:
            return {"success": False, "error": "A student with that email already exists."}
        if "UNIQUE" in msg and "roll_no" in msg:
            return {"success": False, "error": f'Roll number "{data.get("rollNo")}" is already registered.'}
        return {"success": False, "error": msg}


def get_all_students(
    search: str = "",
    department: str = "",
    grade: str = "",
    sort_by: str = "created_at",
    sort_dir: str = "desc",
    page: int = 0,
    page_size: int = 0,
) -> dict:
    """Return filtered, sorted, paginated student list.
    Response shape: { success, data: [...], total }"""
    db = get_db()

    # Allowed sort columns (whitelist to prevent SQL injection)
    allowed_sort = {
        "name": "name", "createdAt": "created_at", "created_at": "created_at",
        "marks": "marks", "grade": "grade", "department": "department",
        "rollNo": "roll_no", "joinDate": "join_date",
    }
    col = allowed_sort.get(sort_by, "created_at")
    direction = "ASC" if sort_dir.lower() == "asc" else "DESC"

    conditions = []
    params: list = []

    if search:
        pattern = f"%{search}%"
        conditions.append("(name LIKE ? OR email LIKE ? OR CAST(id AS TEXT) LIKE ? OR roll_no LIKE ?)")
        params.extend([pattern, pattern, pattern, pattern])
    if department:
        conditions.append("department = ?")
        params.append(department)
    if grade:
        conditions.append("grade = ?")
        params.append(grade)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""

    count_row = db.execute(f"SELECT COUNT(*) FROM students {where}", params).fetchone()
    total = count_row[0]

    query = f"SELECT * FROM students {where} ORDER BY {col} {direction}"
    if page_size > 0:
        offset = (max(page, 1) - 1) * page_size
        query += f" LIMIT {page_size} OFFSET {offset}"

    rows = db.execute(query, params).fetchall()
    return {
        "success": True,
        "data":    [_row_to_student(r) for r in rows],
        "total":   total,
        "page":    page or 1,
        "pageSize": page_size,
    }


def get_student_by_id(student_id: int) -> dict:
    """Fetch a single student. Returns { success, data: student }."""
    db  = get_db()
    row = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if not row:
        return {"success": False, "error": f"Student {student_id} not found."}
    return {"success": True, "data": _row_to_student(row)}


def update_student(student_id: int, data: dict) -> dict:
    """Partially update a student. Returns { success, data: student }."""
    check = get_student_by_id(student_id)
    if not check["success"]:
        return check

    errors = _validate(data, require_all=False)
    if errors:
        return {"success": False, "error": "; ".join(errors)}

    marks = None
    if data.get("marks") not in (None, ""):
        try:
            marks = float(data["marks"])
        except (ValueError, TypeError):
            pass
    grade = _assign_grade(marks) if marks is not None else None

    db = get_db()
    try:
        db.execute(
            """UPDATE students SET
               name             = COALESCE(?, name),
               email            = COALESCE(?, email),
               phone            = COALESCE(?, phone),
               dob              = COALESCE(?, dob),
               address          = COALESCE(?, address),
               roll_no          = COALESCE(?, roll_no),
               department       = COALESCE(?, department),
               marks            = COALESCE(?, marks),
               grade            = COALESCE(?, grade),
               blood_group      = COALESCE(?, blood_group),
               guardian_name    = COALESCE(?, guardian_name),
               guardian_contact = COALESCE(?, guardian_contact),
               join_date        = COALESCE(?, join_date),
               updated_at       = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (
                data.get("name", "").strip() or None,
                data.get("email", "").strip().lower() or None,
                data.get("phone", "").strip() or None,
                data.get("dob") or None,
                data.get("address", "").strip() or None,
                data.get("rollNo", "").strip() or None,
                data.get("department", "").strip() or None,
                marks,
                grade,
                data.get("bloodGroup", "").strip() or None,
                data.get("guardianName", "").strip() or None,
                data.get("guardianContact", "").strip() or None,
                data.get("joinDate") or None,
                student_id,
            ),
        )
        db.commit()
        return {"success": True, "data": get_student_by_id(student_id)["data"]}
    except Exception as exc:
        msg = str(exc)
        if "UNIQUE" in msg and "email" in msg:
            return {"success": False, "error": "That email is already in use."}
        if "UNIQUE" in msg and "roll_no" in msg:
            return {"success": False, "error": "That roll number is already in use."}
        return {"success": False, "error": msg}


def delete_student(student_id: int) -> dict:
    """Delete a student (cascades). Returns { success, data: { id } }."""
    check = get_student_by_id(student_id)
    if not check["success"]:
        return check
    db = get_db()
    db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    return {"success": True, "data": {"id": student_id}}


def get_stats() -> dict:
    """
    Dashboard statistics — matches the shape the GitHub frontend expects:
    { success, data: { total, averageMarks, departments, topScorers,
                       departmentBreakdown } }
    """
    db = get_db()
    rows = db.execute("SELECT department, marks, grade FROM students").fetchall()

    total       = len(rows)
    avg_marks   = 0
    dept_set    = set()
    top_scorers = 0
    dept_map: dict = {}

    if total:
        mark_vals = [r["marks"] for r in rows if r["marks"] is not None]
        avg_marks = round(sum(mark_vals) / len(mark_vals), 1) if mark_vals else 0

    for r in rows:
        dept = r["department"] or "Unassigned"
        dept_set.add(dept)
        dept_map[dept] = dept_map.get(dept, 0) + 1
        if r["grade"] == "A+":
            top_scorers += 1

    return {
        "success": True,
        "data": {
            "total":               total,
            "averageMarks":        avg_marks,
            "departments":         len(dept_set),
            "topScorers":          top_scorers,
            "departmentBreakdown": dept_map,
        },
    }

"""
services/marks_service.py
─────────────────────────
Business logic for adding/updating marks and calculating grades.

Grade scheme (industry-standard):
    90–100  → A+
    80–89   → A
    70–79   → B
    60–69   → C
    50–59   → D
    0–49    → F
"""

from database.db_config import get_db


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def assign_grade(avg_marks: float) -> str:
    """Convert a numeric average into a letter grade."""
    if avg_marks >= 90:
        return "A+"
    elif avg_marks >= 80:
        return "A"
    elif avg_marks >= 70:
        return "B"
    elif avg_marks >= 60:
        return "C"
    elif avg_marks >= 50:
        return "D"
    else:
        return "F"


def add_or_update_marks(student_id: int, course_id: int, marks: float) -> dict:
    """
    Upsert marks for a student in a specific course.
    Student must be enrolled in the course before marks can be added.
    Marks must be in [0, 100].
    """
    # Validate marks range
    try:
        marks = float(marks)
    except (ValueError, TypeError):
        return {"success": False, "error": "Marks must be a number."}

    if not (0 <= marks <= 100):
        return {"success": False, "error": "Marks must be between 0 and 100."}

    db = get_db()

    # Student must be enrolled in the course
    enrolled = db.execute(
        "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
        (student_id, course_id),
    ).fetchone()
    if not enrolled:
        return {
            "success": False,
            "error": "Student is not enrolled in this course. Enroll first.",
        }

    try:
        # INSERT OR REPLACE handles the upsert for the UNIQUE (student_id, course_id) key
        db.execute(
            """INSERT INTO marks (student_id, course_id, marks) VALUES (?, ?, ?)
               ON CONFLICT(student_id, course_id) DO UPDATE SET marks = excluded.marks""",
            (student_id, course_id, marks),
        )
        db.commit()
        return {"success": True, "message": "Marks saved.", "marks": marks}
    except Exception as exc:
        return {"success": False, "error": str(exc)}


def get_student_marks(student_id: int) -> dict:
    """
    Return all marks for a student, plus summary stats
    (total, average, grade).
    """
    db = get_db()
    student = db.execute("SELECT id, name FROM students WHERE id = ?", (student_id,)).fetchone()
    if not student:
        return {"success": False, "error": f"Student {student_id} not found."}

    rows = db.execute(
        """SELECT c.id AS course_id, c.course_name, m.marks
           FROM marks m
           JOIN courses c ON c.id = m.course_id
           WHERE m.student_id = ?
           ORDER BY c.course_name""",
        (student_id,),
    ).fetchall()

    mark_list = [_row_to_dict(r) for r in rows]
    total   = sum(r["marks"] for r in mark_list)
    count   = len(mark_list)
    average = round(total / count, 2) if count else 0.0
    grade   = assign_grade(average) if count else "N/A"

    return {
        "success":  True,
        "marks":    mark_list,
        "total":    round(total, 2),
        "average":  average,
        "grade":    grade,
        "student":  _row_to_dict(student),
    }


def calculate_average(student_id: int) -> dict:
    """Calculate and return just the average + grade for a student."""
    result = get_student_marks(student_id)
    if not result["success"]:
        return result
    return {
        "success": True,
        "average": result["average"],
        "grade":   result["grade"],
    }

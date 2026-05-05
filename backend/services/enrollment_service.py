"""
services/enrollment_service.py
──────────────────────────────
Business logic for enrolling/removing students from courses.
"""

from database.db_config import get_db


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def enroll_student(student_id: int, course_id: int) -> dict:
    """
    Enroll a student in a course.
    Enforces uniqueness: a student cannot be enrolled twice in the same course.
    """
    db = get_db()

    # Verify both records exist before attempting insert
    student = db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    if not student:
        return {"success": False, "error": f"Student {student_id} not found."}

    course = db.execute("SELECT id FROM courses WHERE id = ?", (course_id,)).fetchone()
    if not course:
        return {"success": False, "error": f"Course {course_id} not found."}

    try:
        db.execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
            (student_id, course_id),
        )
        db.commit()
        return {"success": True, "message": f"Student {student_id} enrolled in course {course_id}."}
    except Exception:
        return {"success": False, "error": "Student is already enrolled in this course."}


def get_student_courses(student_id: int) -> dict:
    """Return all courses (with enrollment date) for a given student."""
    db = get_db()
    student = db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    if not student:
        return {"success": False, "error": f"Student {student_id} not found."}

    rows = db.execute(
        """SELECT c.id, c.course_name, c.credits, c.instructor_name, e.enrolled_at
           FROM enrollments e
           JOIN courses c ON c.id = e.course_id
           WHERE e.student_id = ?
           ORDER BY c.course_name""",
        (student_id,),
    ).fetchall()

    return {"success": True, "courses": [_row_to_dict(r) for r in rows]}


def remove_enrollment(student_id: int, course_id: int) -> dict:
    """Remove a student's enrollment from a course."""
    db = get_db()
    row = db.execute(
        "SELECT id FROM enrollments WHERE student_id = ? AND course_id = ?",
        (student_id, course_id),
    ).fetchone()

    if not row:
        return {"success": False, "error": "Enrollment not found."}

    db.execute(
        "DELETE FROM enrollments WHERE student_id = ? AND course_id = ?",
        (student_id, course_id),
    )
    db.commit()
    return {"success": True, "message": "Enrollment removed."}


def get_students_by_course(course_id: int) -> dict:
    """Return all students enrolled in a given course."""
    db = get_db()
    rows = db.execute(
        """SELECT s.id, s.name, s.email, e.enrolled_at
           FROM enrollments e
           JOIN students s ON s.id = e.student_id
           WHERE e.course_id = ?
           ORDER BY s.name""",
        (course_id,),
    ).fetchall()
    return {"success": True, "students": [_row_to_dict(r) for r in rows]}

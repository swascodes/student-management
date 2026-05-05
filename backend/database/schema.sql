-- Student Manager – SQLite Schema
-- Enables foreign key enforcement (must be called per connection)

PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────
-- Table: students
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id         INTEGER   PRIMARY KEY AUTOINCREMENT,
    name       TEXT      NOT NULL,
    email      TEXT      UNIQUE NOT NULL,
    phone      TEXT,
    dob        DATE,
    address    TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- Table: courses
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS courses (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name     TEXT    NOT NULL,
    credits         INTEGER NOT NULL CHECK (credits > 0),
    instructor_name TEXT    NOT NULL
);

-- ─────────────────────────────────────────
-- Table: enrollments  (Many-to-Many: students ↔ courses)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id          INTEGER   PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER   NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id   INTEGER   NOT NULL REFERENCES courses(id)  ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, course_id)
);

-- ─────────────────────────────────────────
-- Table: marks
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS marks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id  INTEGER NOT NULL REFERENCES courses(id)  ON DELETE CASCADE,
    marks      REAL    NOT NULL CHECK (marks >= 0 AND marks <= 100),
    UNIQUE (student_id, course_id)
);

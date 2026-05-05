-- Student Manager – SQLite Schema v2
-- Adds extended student fields + admins table for auth

PRAGMA foreign_keys = ON;

-- ─────────────────────────────────────────
-- Table: students (v2 — extended fields)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS students (
    id               INTEGER   PRIMARY KEY AUTOINCREMENT,
    name             TEXT      NOT NULL,
    email            TEXT      UNIQUE NOT NULL,
    phone            TEXT,
    dob              DATE,
    address          TEXT,
    -- Extended fields (GitHub frontend compatible)
    roll_no          TEXT      UNIQUE,
    department       TEXT,
    marks            REAL      CHECK (marks IS NULL OR (marks >= 0 AND marks <= 100)),
    grade            TEXT,
    blood_group      TEXT,
    guardian_name    TEXT,
    guardian_contact TEXT,
    join_date        DATE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
-- Table: enrollments  (Many-to-Many)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS enrollments (
    id          INTEGER   PRIMARY KEY AUTOINCREMENT,
    student_id  INTEGER   NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id   INTEGER   NOT NULL REFERENCES courses(id)  ON DELETE CASCADE,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (student_id, course_id)
);

-- ─────────────────────────────────────────
-- Table: marks (per-course marks)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS marks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_id  INTEGER NOT NULL REFERENCES courses(id)  ON DELETE CASCADE,
    marks      REAL    NOT NULL CHECK (marks >= 0 AND marks <= 100),
    UNIQUE (student_id, course_id)
);

-- ─────────────────────────────────────────
-- Table: admins (for login/signup)
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS admins (
    id            INTEGER   PRIMARY KEY AUTOINCREMENT,
    username      TEXT      NOT NULL,
    email         TEXT      UNIQUE NOT NULL,
    password_hash TEXT      NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ─────────────────────────────────────────
-- Table: sessions
-- ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS sessions (
    token      TEXT      PRIMARY KEY,
    admin_id   INTEGER   NOT NULL REFERENCES admins(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

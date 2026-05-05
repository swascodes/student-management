# 🎓 Student Manager

A production-ready **Student Management Platform** built with Python (Flask) + SQLite + Vanilla HTML/CSS/JS.

> Manage student lifecycle, course allocations, enrollments, and academic performance — all from a clean, modern web interface.

---

## 📸 Preview

| Dashboard | Students | Student Detail |
|-----------|----------|----------------|
| Live stats, quick actions, recent students | Search, filter by course, CRUD | Profile, enrolled courses, marks + grades |

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 👨‍🎓 **Student CRUD** | Add, view, edit, delete students with full validation |
| 📚 **Course Management** | Create and manage courses with credit and instructor info |
| 🔗 **Enrollment System** | Many-to-many student ↔ course assignment |
| 📝 **Marks & Grades** | Add/update marks per course; auto-calculates average and grade |
| 🔍 **Search & Filter** | Search students by name/ID; filter by enrolled course |
| 🎨 **Premium Dark UI** | Glassmorphism design with smooth animations |
| ✅ **Input Validation** | Client-side + server-side validation with clear error messages |
| 🔁 **Toast Notifications** | Real-time feedback for every action |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.10+, Flask 3.x |
| Database | SQLite (WAL mode, FK constraints) |
| Frontend | HTML5, CSS3, Vanilla JavaScript (Fetch API) |
| Fonts | Google Fonts – Inter |
| CORS | flask-cors |

---

## 🏗️ System Architecture

```
Browser (HTML/CSS/JS)
       │
       │  HTTP (REST API)
       ▼
  Flask App (app.py)
       │
  ┌────┴────────────┐
  │    Blueprints    │
  │  students_bp     │
  │  courses_bp      │
  │  enrollments_bp  │
  │  marks_bp        │
  └────┬────────────┘
       │
  ┌────┴────────────┐
  │    Services      │
  │  student_svc     │  ← Business logic
  │  course_svc      │
  │  enrollment_svc  │
  │  marks_svc       │
  └────┬────────────┘
       │
  ┌────┴────────────┐
  │  SQLite Database │
  │  (WAL mode)      │
  └─────────────────┘
```

---

## 🗄️ Database Schema

### `students`
| Column | Type | Constraint |
|--------|------|-----------|
| id | INTEGER | PK AUTOINCREMENT |
| name | TEXT | NOT NULL |
| email | TEXT | UNIQUE NOT NULL |
| phone | TEXT | |
| dob | DATE | |
| address | TEXT | |
| created_at | TIMESTAMP | DEFAULT NOW |

### `courses`
| Column | Type | Constraint |
|--------|------|-----------|
| id | INTEGER | PK AUTOINCREMENT |
| course_name | TEXT | NOT NULL |
| credits | INTEGER | NOT NULL, > 0 |
| instructor_name | TEXT | NOT NULL |

### `enrollments`
| Column | Type | Constraint |
|--------|------|-----------|
| id | INTEGER | PK AUTOINCREMENT |
| student_id | INTEGER | FK → students(id) CASCADE |
| course_id | INTEGER | FK → courses(id) CASCADE |
| enrolled_at | TIMESTAMP | DEFAULT NOW |
| | UNIQUE | (student_id, course_id) |

### `marks`
| Column | Type | Constraint |
|--------|------|-----------|
| id | INTEGER | PK AUTOINCREMENT |
| student_id | INTEGER | FK → students(id) CASCADE |
| course_id | INTEGER | FK → courses(id) CASCADE |
| marks | REAL | CHECK 0–100 |
| | UNIQUE | (student_id, course_id) |

---

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or higher
- pip

> **No MySQL required!** This project uses SQLite — zero configuration, zero external service.

---

### 1. Clone / Navigate to project

```bash
cd e:/workspace/student-manager
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask server

```bash
cd backend
python app.py
```

The server starts at **http://127.0.0.1:5000**

The SQLite database is auto-created at `backend/database/student_manager.db` on first run.

### 5. Open the app

Navigate to **http://127.0.0.1:5000** in your browser.

---

## 📡 API Endpoints

### Students

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/students` | Get all students (supports `?search=`) |
| `POST` | `/api/students` | Create new student |
| `GET` | `/api/students/<id>` | Get student by ID |
| `PUT` | `/api/students/<id>` | Update student |
| `DELETE` | `/api/students/<id>` | Delete student (cascades) |

### Courses

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/courses` | Get all courses |
| `POST` | `/api/courses` | Create course |
| `GET` | `/api/courses/<id>` | Get course by ID |
| `PUT` | `/api/courses/<id>` | Update course |
| `DELETE` | `/api/courses/<id>` | Delete course |

### Enrollments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/enrollments` | Enroll student in course |
| `GET` | `/api/enrollments/student/<id>` | Get courses for a student |
| `GET` | `/api/enrollments/course/<id>` | Get students in a course |
| `DELETE` | `/api/enrollments/<sid>/<cid>` | Remove enrollment |

### Marks

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/marks` | Add or update marks |
| `GET` | `/api/marks/<student_id>` | Get all marks + total/avg/grade |
| `GET` | `/api/marks/<student_id>/summary` | Get just average + grade |

---

### Example API Calls

```bash
# Create a student
curl -X POST http://localhost:5000/api/students \
  -H "Content-Type: application/json" \
  -d '{"name":"Aarav Sharma","email":"aarav@example.com","phone":"9876543210"}'

# Enroll in a course
curl -X POST http://localhost:5000/api/enrollments \
  -H "Content-Type: application/json" \
  -d '{"student_id":1,"course_id":2}'

# Add marks
curl -X POST http://localhost:5000/api/marks \
  -H "Content-Type: application/json" \
  -d '{"student_id":1,"course_id":2,"marks":87.5}'
```

---

## 📁 Folder Structure

```
student-manager/
├── backend/
│   ├── app.py                     # Flask app factory + entry point
│   ├── routes/
│   │   ├── student_routes.py      # Student REST endpoints
│   │   ├── course_routes.py       # Course REST endpoints
│   │   ├── enrollment_routes.py   # Enrollment REST endpoints
│   │   └── marks_routes.py        # Marks REST endpoints
│   ├── services/
│   │   ├── student_service.py     # Student business logic
│   │   ├── course_service.py      # Course business logic
│   │   ├── enrollment_service.py  # Enrollment business logic
│   │   └── marks_service.py       # Marks + grading logic
│   └── database/
│       ├── db_config.py           # Connection management + schema init
│       ├── schema.sql             # DDL for all 4 tables
│       └── student_manager.db     # SQLite DB (auto-created)
├── frontend/
│   ├── index.html                 # Dashboard
│   ├── students.html              # Student list + search
│   ├── student_detail.html        # Student profile + marks
│   ├── add_student.html           # Add / Edit student
│   ├── courses.html               # Course list
│   ├── add_course.html            # Add / Edit course
│   ├── enroll.html                # Enrollment management
│   ├── css/style.css              # Global design system
│   └── js/api.js                  # Fetch API client + utilities
├── requirements.txt
└── README.md
```

---

## 🎓 Grade Scheme

| Range | Grade |
|-------|-------|
| 90–100 | A+ |
| 80–89 | A |
| 70–79 | B |
| 60–69 | C |
| 50–59 | D |
| 0–49 | F |

---

## 🔒 Validation & Constraints

- **No duplicate emails** — enforced at DB level (UNIQUE) + service layer
- **No duplicate enrollments** — UNIQUE(student_id, course_id) in enrollments
- **Marks range** — CHECK constraint 0–100 + service validation
- **FK cascade** — Deleting a student removes enrollments & marks; same for courses
- **Student must be enrolled** before marks can be recorded

---

## 🌱 Future Enhancements

- [ ] **Admin Authentication** — JWT-based login system
- [ ] **Pagination** — For large student/course lists
- [ ] **CSV Export** — Export student reports
- [ ] **Dashboard Analytics** — Charts for grade distribution
- [ ] **Attendance Module** — Track class attendance
- [ ] **Postman Collection** — Full API test suite
- [ ] **Docker** — Containerized deployment
- [ ] **PostgreSQL Migration** — Production-grade database

---

## 👨‍💻 Author

Built as a production-ready MVP for educational institution management.

---

*Happy Learning! 🎓*

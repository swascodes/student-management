# Student Management System

A modern, production-level **Student Management System** dashboard built with HTML, CSS, and JavaScript.

## 🚀 Live Demo
Open `index.html` in any browser, or serve locally:
```bash
npx serve . -p 4999
```

## 📁 Project Structure

| File | Purpose |
|---|---|
| `index.html` | Dashboard — stats, recent students, dept chart |
| `add.html` | Add Student — form with live validation |
| `manage.html` | Manage Students — sortable table, edit/delete |
| `search.html` | Search — live search, dept chips, profile modal |
| `style.css` | Full design system — dark mode, animations |
| `config.js` | **API config** — toggle mock ↔ real backend |
| `api.js` | **API service layer** — all data operations |
| `script.js` | Shared utilities — theme, toast, sidebar |

## 🔌 Connecting a Real Backend

1. Open `config.js`
2. Set `USE_MOCK_API: false`
3. Set `API_BASE_URL` to your server (e.g. `http://localhost:8080/api/v1`)

### Expected REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/students` | List all students (supports `?search`, `?department`, `?grade`, `?sortBy`, `?sortDir`) |
| `GET` | `/students/:id` | Get single student |
| `POST` | `/students` | Create student |
| `PUT` | `/students/:id` | Update student |
| `DELETE` | `/students/:id` | Delete student |
| `GET` | `/students/stats` | Dashboard stats |

### Student Object Shape
```json
{
  "id": "string",
  "name": "string",
  "rollNo": "string",
  "department": "string",
  "email": "string",
  "phone": "string",
  "marks": 85,
  "grade": "A",
  "joinDate": "2024-01-01",
  "address": "string",
  "createdAt": 1711558474000,
  "updatedAt": 1711558474000
}
```

### Response Format
```json
{ "success": true, "data": { ... } }
// Error:
{ "success": false, "message": "Error description" }
```

## ✨ Features
- 📊 **Dashboard** — live stats, department breakdown, activity feed
- ➕ **Add Student** — real-time validation, grade auto-calculation
- 📋 **Manage Students** — sort by any column, multi-filter, edit modal, delete confirm
- 🔍 **Search** — live search, dept chips, profile cards, hover profiles
- 🌙 **Dark Mode** — persists via localStorage
- 🔔 **Toast Notifications** — success/error/info
- 📱 **Responsive** — collapsible sidebar on mobile

## 🛠️ Tech Stack
- Vanilla HTML, CSS, JavaScript (no build step)
- Font Awesome 6 icons
- localStorage mock backend (swappable with real API)

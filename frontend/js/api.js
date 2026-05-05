/**
 * js/api.js
 * ─────────
 * Thin fetch wrapper around the Student Manager REST API.
 * All functions return { success, data | error } objects.
 */

// API base — relative path works both locally (Flask serves frontend)
// and in production (Render, same origin). No env config needed.
const API_BASE = "/api";

/**
 * Core fetch helper.
 * @param {string} path    - API path (e.g., "/students")
 * @param {object} options - Fetch options (method, body, etc.)
 * @returns {Promise<object>}
 */
async function apiFetch(path, options = {}) {
  const defaults = {
    headers: { "Content-Type": "application/json" },
  };
  try {
    const res  = await fetch(`${API_BASE}${path}`, { ...defaults, ...options });
    const json = await res.json();
    return json;
  } catch (err) {
    return { success: false, error: err.message };
  }
}

/* ── Students ─────────────────────────────────────────────────── */
const StudentsAPI = {
  getAll:    (search = "")      => apiFetch(`/students${search ? `?search=${encodeURIComponent(search)}` : ""}`),
  getById:   (id)               => apiFetch(`/students/${id}`),
  create:    (data)             => apiFetch("/students",    { method: "POST",   body: JSON.stringify(data) }),
  update:    (id, data)         => apiFetch(`/students/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete:    (id)               => apiFetch(`/students/${id}`, { method: "DELETE" }),
};

/* ── Courses ──────────────────────────────────────────────────── */
const CoursesAPI = {
  getAll:  ()         => apiFetch("/courses"),
  getById: (id)       => apiFetch(`/courses/${id}`),
  create:  (data)     => apiFetch("/courses",    { method: "POST",   body: JSON.stringify(data) }),
  update:  (id, data) => apiFetch(`/courses/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  delete:  (id)       => apiFetch(`/courses/${id}`, { method: "DELETE" }),
};

/* ── Enrollments ─────────────────────────────────────────────── */
const EnrollmentsAPI = {
  enroll:         (student_id, course_id) => apiFetch("/enrollments", { method: "POST", body: JSON.stringify({ student_id, course_id }) }),
  getForStudent:  (student_id)            => apiFetch(`/enrollments/student/${student_id}`),
  getForCourse:   (course_id)             => apiFetch(`/enrollments/course/${course_id}`),
  remove:         (student_id, course_id) => apiFetch(`/enrollments/${student_id}/${course_id}`, { method: "DELETE" }),
};

/* ── Marks ───────────────────────────────────────────────────── */
const MarksAPI = {
  save:       (student_id, course_id, marks) => apiFetch("/marks", { method: "POST", body: JSON.stringify({ student_id, course_id, marks }) }),
  getForStudent: (student_id)                => apiFetch(`/marks/${student_id}`),
  getSummary:    (student_id)                => apiFetch(`/marks/${student_id}/summary`),
};

/* ── Toast Notifications ─────────────────────────────────────── */
function showToast(message, type = "success") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === "success" ? "✓" : "✕"}</span> ${message}`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = "slideIn 0.3s var(--ease) reverse";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

/**
 * Render a loading skeleton into a table body.
 * @param {HTMLElement} tbody
 * @param {number} cols
 */
function renderTableSkeleton(tbody, cols = 5) {
  tbody.innerHTML = Array.from({ length: 4 }, () =>
    `<tr>${Array.from({ length: cols }, () =>
      `<td><div class="skeleton"></div></td>`
    ).join("")}</tr>`
  ).join("");
}

/**
 * Get a letter-grade CSS class.
 */
function gradeClass(grade) {
  return `badge badge-grade-${grade}`;
}

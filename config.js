/* ============================================================
   Student Management System — config.js
   Central configuration. Change these values to connect your
   real backend. Set USE_MOCK_API = false when backend is ready.
   ============================================================ */

const SMS_CONFIG = {
  /**
   * ─── BACKEND TOGGLE ────────────────────────────────────────
   * true  → use localStorage (demo / offline mode)
   * false → use real HTTP REST API at API_BASE_URL
   */
  USE_MOCK_API: true,

  /**
   * ─── YOUR REST API BASE URL ────────────────────────────────
   * Example: 'http://localhost:8080/api/v1'
   *          'https://api.yourschool.com/v1'
   * The API client will call:
   *   GET    {BASE_URL}/students
   *   GET    {BASE_URL}/students/:id
   *   POST   {BASE_URL}/students
   *   PUT    {BASE_URL}/students/:id
   *   DELETE {BASE_URL}/students/:id
   *   GET    {BASE_URL}/students/stats
   */
  API_BASE_URL: 'http://localhost:8080/api/v1',

  /**
   * ─── AUTH ──────────────────────────────────────────────────
   * Set AUTH_TOKEN to send Authorization: Bearer <token> header.
   * Leave empty string to omit the header.
   * You can also set this at runtime:
   *   SMS_CONFIG.AUTH_TOKEN = localStorage.getItem('auth_token');
   */
  AUTH_TOKEN: '',

  /**
   * ─── REQUEST TIMEOUT (ms) ──────────────────────────────────
   */
  TIMEOUT_MS: 10000,

  /**
   * ─── PAGINATION ────────────────────────────────────────────
   * Default page size sent to the API.
   * Set to 0 to disable pagination (fetch all).
   */
  PAGE_SIZE: 50,

  /**
   * ─── EXPECTED API RESPONSE SHAPE ───────────────────────────
   *
   * List endpoint (GET /students) should return:
   * {
   *   "success": true,
   *   "data": [ ...student objects ],
   *   "total": 120,          // optional, for pagination
   *   "page": 1,             // optional
   *   "pageSize": 50         // optional
   * }
   *
   * Single / mutate endpoints should return:
   * {
   *   "success": true,
   *   "data": { ...student object }
   * }
   *
   * Stats endpoint (GET /students/stats) should return:
   * {
   *   "success": true,
   *   "data": {
   *     "total": 120,
   *     "averageMarks": 74.3,
   *     "departments": 10,
   *     "topScorers": 8
   *   }
   * }
   *
   * Error responses should return HTTP 4xx/5xx with:
   * {
   *   "success": false,
   *   "message": "Human-readable error description"
   * }
   *
   * Student object shape:
   * {
   *   "id":         "string",
   *   "name":       "string",
   *   "rollNo":     "string",
   *   "department": "string",
   *   "email":      "string",
   *   "phone":      "string",
   *   "marks":      number (0–100),
   *   "grade":      "string",
   *   "joinDate":   "YYYY-MM-DD",
   *   "address":    "string",
   *   "createdAt":  "ISO 8601 string or Unix ms",
   *   "updatedAt":  "ISO 8601 string or Unix ms"
   * }
   */
};

/* ── Runtime helper: update auth token after login ─────────── */
function setAuthToken(token) {
  SMS_CONFIG.AUTH_TOKEN = token;
  if (token) {
    localStorage.setItem('sms_auth_token', token);
  } else {
    localStorage.removeItem('sms_auth_token');
  }
}

/* Auto-load token from storage on boot */
(function () {
  const saved = localStorage.getItem('sms_auth_token');
  if (saved) SMS_CONFIG.AUTH_TOKEN = saved;
})();

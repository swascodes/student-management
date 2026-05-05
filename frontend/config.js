/* ============================================================
   Student Management System — config.js
   Now wired to the Flask backend.
   ============================================================ */

const SMS_CONFIG = {
  /**
   * false = use the real Flask REST API (backend is live)
   */
  USE_MOCK_API: false,

  /**
   * Relative URL — works both locally (Flask serves everything)
   * and on Render (same origin, no CORS issues).
   */
  API_BASE_URL: '/api',

  /**
   * Auth token — auto-loaded from localStorage on boot.
   * Updated by setAuthToken() after login.
   */
  AUTH_TOKEN: '',

  TIMEOUT_MS: 10000,
  PAGE_SIZE:  50,
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

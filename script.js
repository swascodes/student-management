/* ============================================================
   Student Management System — script.js
   Shared utilities: theme, sidebar, UI helpers.
   Data operations have moved to api.js / ApiService.
   ============================================================ */

'use strict';

const THEME_KEY = 'sms_theme';

const DEPARTMENTS = [
  'Computer Science', 'Mathematics', 'Physics', 'Chemistry',
  'Biology', 'Engineering', 'Business Administration',
  'Economics', 'Psychology', 'Literature',
];

/* ── Grade / Display Helpers ────────────────────────────────── */
function computeGrade(marks) {
  const m = Number(marks);
  if (m >= 90) return 'A+';
  if (m >= 80) return 'A';
  if (m >= 70) return 'B+';
  if (m >= 60) return 'B';
  if (m >= 50) return 'C';
  if (m >= 40) return 'D';
  return 'F';
}

function gradeClass(grade) {
  if (!grade) return '';
  if (grade.startsWith('A')) return 'grade-a';
  if (grade.startsWith('B')) return 'grade-b';
  if (grade.startsWith('C')) return 'grade-c';
  return 'grade-f';
}

function deptBadgeClass(dept) {
  const map = {
    'Computer Science':        'badge-primary',
    'Mathematics':             'badge-info',
    'Physics':                 'badge-warning',
    'Chemistry':               'badge-success',
    'Biology':                 'badge-success',
    'Engineering':             'badge-primary',
    'Business Administration': 'badge-warning',
    'Economics':               'badge-info',
    'Psychology':              'badge-danger',
    'Literature':              'badge-danger',
  };
  return map[dept] || 'badge-primary';
}

function initials(name = '') {
  return (name || '?').split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

function formatDate(ts) {
  if (!ts) return '—';
  const d = new Date(typeof ts === 'number' ? ts : ts);
  return isNaN(d) ? '—' : d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

function timeSince(ts) {
  const s = Math.floor((Date.now() - Number(ts)) / 1000);
  if (s < 60)    return `${s}s ago`;
  if (s < 3600)  return `${Math.floor(s / 60)}m ago`;
  if (s < 86400) return `${Math.floor(s / 3600)}h ago`;
  return `${Math.floor(s / 86400)}d ago`;
}

function escapeHtml(str) {
  const d = document.createElement('div');
  d.textContent = String(str ?? '');
  return d.innerHTML;
}

/* ── Department Dropdowns ───────────────────────────────────── */
function populateDeptFilter(selectEl, includeAll = true) {
  if (!selectEl) return;
  selectEl.innerHTML = '';
  if (includeAll) {
    const opt = Object.assign(document.createElement('option'), { value: '', textContent: 'All Departments' });
    selectEl.appendChild(opt);
  }
  DEPARTMENTS.forEach(d => selectEl.appendChild(Object.assign(document.createElement('option'), { value: d, textContent: d })));
}

function populateDeptSelect(selectEl, selected = '') {
  if (!selectEl) return;
  selectEl.innerHTML = '<option value="" disabled>Select Department</option>';
  DEPARTMENTS.forEach(d => {
    const opt = Object.assign(document.createElement('option'), { value: d, textContent: d });
    if (d === selected) opt.selected = true;
    selectEl.appendChild(opt);
  });
}

/* ── Theme ──────────────────────────────────────────────────── */
function initTheme() {
  const saved = localStorage.getItem(THEME_KEY) || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcon(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next    = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem(THEME_KEY, next);
  updateThemeIcon(next);
}

function updateThemeIcon(theme) {
  const btn = document.getElementById('dark-toggle');
  if (!btn) return;
  btn.innerHTML = theme === 'dark'
    ? '<i class="fa-solid fa-sun"></i>'
    : '<i class="fa-solid fa-moon"></i>';
  btn.title = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode';
}

/* ── Sidebar ────────────────────────────────────────────────── */
function initSidebar() {
  const toggle  = document.getElementById('menu-toggle');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  if (!toggle || !sidebar) return;

  toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
  if (overlay) overlay.addEventListener('click', () => sidebar.classList.remove('open'));
  sidebar.querySelectorAll('.nav-link').forEach(link =>
    link.addEventListener('click', () => { if (window.innerWidth <= 900) sidebar.classList.remove('open'); })
  );
}

function setActiveNav() {
  const path = window.location.pathname.split('/').pop() || 'dashboard.html';
  document.querySelectorAll('.nav-link').forEach(link => {
    const href = (link.getAttribute('href') || '').split('/').pop();
    link.classList.toggle('active', href === path || (path === '' && href === 'dashboard.html'));
  });
}

/* ── Toast ──────────────────────────────────────────────────── */
function showToast(type, title, message = '') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const icons = { success: 'fa-circle-check', error: 'fa-circle-xmark', warning: 'fa-triangle-exclamation', info: 'fa-circle-info' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <div class="toast-icon"><i class="fa-solid ${icons[type] || icons.info}"></i></div>
    <div class="toast-content">
      <div class="toast-title">${escapeHtml(title)}</div>
      ${message ? `<div class="toast-msg">${escapeHtml(message)}</div>` : ''}
    </div>
    <button class="toast-close" aria-label="Close"><i class="fa-solid fa-xmark"></i></button>`;
  container.appendChild(toast);
  const close = () => { toast.classList.add('removing'); setTimeout(() => toast.remove(), 320); };
  toast.querySelector('.toast-close').addEventListener('click', close);
  setTimeout(close, 4500);
}

/* ── Confirm Dialog ─────────────────────────────────────────── */
function showConfirm({ title, message, confirmLabel = 'Delete', onConfirm }) {
  let overlay = document.getElementById('confirm-overlay');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id        = 'confirm-overlay';
    overlay.className = 'modal-overlay';
    overlay.innerHTML = `
      <div class="modal confirm-modal">
        <div class="modal-body">
          <div class="confirm-icon"><i class="fa-solid fa-trash-can"></i></div>
          <h3 id="confirm-title"></h3>
          <p id="confirm-msg"></p>
        </div>
        <div class="modal-footer">
          <button class="btn btn-outline" id="confirm-cancel">Cancel</button>
          <button class="btn btn-danger" id="confirm-ok">Delete</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
  }

  overlay.querySelector('#confirm-title').textContent  = title;
  overlay.querySelector('#confirm-msg').textContent    = message;
  overlay.querySelector('#confirm-ok').textContent     = confirmLabel;

  const hide = () => { overlay.classList.remove('show'); document.body.style.overflow = ''; };

  // Replace buttons to clear old listeners
  ['confirm-ok', 'confirm-cancel'].forEach(id => {
    const old = overlay.querySelector('#' + id);
    const n   = old.cloneNode(true);
    old.replaceWith(n);
  });

  overlay.querySelector('#confirm-ok').addEventListener('click', () => { hide(); onConfirm(); });
  overlay.querySelector('#confirm-cancel').addEventListener('click', hide);
  overlay.addEventListener('click', e => { if (e.target === overlay) hide(); });

  overlay.classList.add('show');
  document.body.style.overflow = 'hidden';
}

/* ── Loading Button Helper ──────────────────────────────────── */
function setButtonLoading(btn, loading, originalHtml) {
  if (loading) {
    btn.disabled   = true;
    btn._origHtml  = btn.innerHTML;
    btn.innerHTML  = '<i class="fa-solid fa-spinner fa-spin"></i> Please wait…';
  } else {
    btn.disabled  = false;
    btn.innerHTML = originalHtml ?? btn._origHtml ?? btn.innerHTML;
  }
}

/* ── Skeleton Loader HTML ───────────────────────────────────── */
function skeletonRows(cols = 6, rows = 5) {
  const cells = `<td colspan="${cols}">
    <div style="display:flex;gap:12px;align-items:center;padding:4px 0;">
      <div style="width:36px;height:36px;border-radius:50%;background:var(--border);flex-shrink:0;animation:pulse 1.4s ease infinite;"></div>
      <div style="flex:1;">
        <div style="height:12px;border-radius:4px;background:var(--border);margin-bottom:6px;width:60%;animation:pulse 1.4s ease infinite;"></div>
        <div style="height:10px;border-radius:4px;background:var(--border);width:40%;animation:pulse 1.4s ease .1s infinite;"></div>
      </div>
    </div>
  </td>`;
  return Array.from({ length: rows }, () => `<tr>${cells}</tr>`).join('');
}

/* ── API Mode Banner ────────────────────────────────────────── */
function renderApiModeBanner() {
  const existing = document.getElementById('api-mode-banner');
  if (existing) existing.remove();

  const bar = document.createElement('div');
  bar.id = 'api-mode-banner';

  if (SMS_CONFIG.USE_MOCK_API) {
    bar.style.cssText = `
      position:fixed; bottom:0; left:var(--sidebar-w); right:0; z-index:500;
      background:linear-gradient(90deg,#f59e0b,#d97706); color:#fff;
      font-size:12px; font-weight:600; padding:7px 20px;
      display:flex; align-items:center; gap:8px;
      box-shadow:0 -2px 8px rgba(0,0,0,.1);
      transition:left .3s ease;`;
    bar.innerHTML = `
      <i class="fa-solid fa-flask"></i>
      <span>DEMO MODE — using localStorage</span>
      <span style="opacity:.7;">·</span>
      <span>To connect your backend: set <code style="background:rgba(0,0,0,.2);padding:1px 5px;border-radius:3px;">USE_MOCK_API = false</code> in <strong>config.js</strong></span>
      <button onclick="this.parentElement.style.display='none'" style="margin-left:auto;background:none;border:none;color:#fff;cursor:pointer;font-size:15px;" aria-label="Dismiss">✕</button>`;
  } else {
    bar.style.cssText = `
      position:fixed; bottom:0; left:var(--sidebar-w); right:0; z-index:500;
      background:linear-gradient(90deg,#10b981,#059669); color:#fff;
      font-size:12px; font-weight:600; padding:7px 20px;
      display:flex; align-items:center; gap:8px;
      transition:left .3s ease;`;
    bar.innerHTML = `
      <i class="fa-solid fa-plug-circle-check"></i>
      <span>LIVE MODE — connected to <code style="background:rgba(0,0,0,.2);padding:1px 5px;border-radius:3px;">${escapeHtml(SMS_CONFIG.API_BASE_URL)}</code></span>
      <button onclick="this.parentElement.style.display='none'" style="margin-left:auto;background:none;border:none;color:#fff;cursor:pointer;font-size:15px;" aria-label="Dismiss">✕</button>`;
  }

  document.body.appendChild(bar);

  // Adjust banner left when sidebar is hidden on mobile
  const updateBannerLeft = () => {
    bar.style.left = window.innerWidth <= 900 ? '0' : 'var(--sidebar-w)';
  };
  window.addEventListener('resize', updateBannerLeft);
  updateBannerLeft();
}

/* ── DOMContentLoaded — runs on every page ──────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  seedDemoDataIfEmpty();   // defined in api.js
  initTheme();
  initSidebar();
  setActiveNav();
  renderApiModeBanner();

  const darkBtn = document.getElementById('dark-toggle');
  if (darkBtn) darkBtn.addEventListener('click', toggleTheme);
});

/* ============================================================
   Student Management System — api.js
   Unified API service layer.
   • USE_MOCK_API = true  → reads/writes localStorage (demo)
   • USE_MOCK_API = false → sends real HTTP requests to your
                            backend at SMS_CONFIG.API_BASE_URL
   ============================================================ */

'use strict';

/* ─────────────────────────────────────────────────────────────
   SECTION 1 — HTTP CLIENT
   A thin fetch wrapper that adds auth headers, timeout,
   and normalises responses/errors.
───────────────────────────────────────────────────────────── */

/**
 * Core HTTP request helper.
 * @param {string} method  - GET | POST | PUT | PATCH | DELETE
 * @param {string} path    - e.g. '/students' or '/students/123'
 * @param {object} [body]  - JSON body for POST/PUT requests
 * @returns {Promise<any>} - resolves with response `data` field
 */
async function httpRequest(method, path, body = null) {
  const url = SMS_CONFIG.API_BASE_URL.replace(/\/$/, '') + path;

  const headers = { 'Content-Type': 'application/json' };
  if (SMS_CONFIG.AUTH_TOKEN) {
    headers['Authorization'] = `Bearer ${SMS_CONFIG.AUTH_TOKEN}`;
  }

  const options = { method, headers };
  if (body !== null) options.body = JSON.stringify(body);

  // Timeout via AbortController
  const controller = new AbortController();
  const timer      = setTimeout(() => controller.abort(), SMS_CONFIG.TIMEOUT_MS);
  options.signal   = controller.signal;

  let response;
  try {
    response = await fetch(url, options);
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      throw new ApiError('Request timed out. Please try again.', 408);
    }
    throw new ApiError(`Network error: ${err.message}`, 0);
  }
  clearTimeout(timer);

  let json;
  try {
    json = await response.json();
  } catch {
    throw new ApiError(`Invalid JSON from server (${response.status})`, response.status);
  }

  if (!response.ok || json.success === false) {
    throw new ApiError(
      json.message || `Server error ${response.status}`,
      response.status,
      json
    );
  }

  return json.data ?? json; // support both { success, data } and bare response
}

/** Custom error class for API errors */
class ApiError extends Error {
  constructor(message, status = 0, raw = null) {
    super(message);
    this.name   = 'ApiError';
    this.status = status;
    this.raw    = raw;
  }
}

/* ─────────────────────────────────────────────────────────────
   SECTION 2 — MOCK BACKEND (localStorage)
   These functions mirror exactly what a real API should do.
   They are used when SMS_CONFIG.USE_MOCK_API === true.
───────────────────────────────────────────────────────────── */

const STORAGE_KEY  = 'sms_students';
const ACTIVITY_KEY = 'sms_activity';

/* ── Helpers ── */
function _load()         { try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || []; } catch { return []; } }
function _save(arr)      { localStorage.setItem(STORAGE_KEY, JSON.stringify(arr)); }
function _genId()        { return Date.now().toString(36) + Math.random().toString(36).slice(2,7); }
function _grade(marks)   {
  const m = Number(marks);
  if (m >= 90) return 'A+';
  if (m >= 80) return 'A';
  if (m >= 70) return 'B+';
  if (m >= 60) return 'B';
  if (m >= 50) return 'C';
  if (m >= 40) return 'D';
  return 'F';
}

function _simulateDelay() {
  // Simulate network latency so the UI loading states are visible
  return new Promise(resolve => setTimeout(resolve, 120));
}

const MOCK = {

  async listStudents({ search = '', department = '', grade = '', sortBy = 'createdAt', sortDir = 'desc', page = 1, pageSize = 0 } = {}) {
    await _simulateDelay();
    let students = _load();

    // Filter
    if (search)     students = students.filter(s =>
      s.name.toLowerCase().includes(search.toLowerCase())       ||
      s.rollNo.toLowerCase().includes(search.toLowerCase())     ||
      s.email.toLowerCase().includes(search.toLowerCase())      ||
      (s.department||'').toLowerCase().includes(search.toLowerCase())
    );
    if (department) students = students.filter(s => s.department === department);
    if (grade)      students = students.filter(s => s.grade === grade);

    // Sort
    students = [...students].sort((a, b) => {
      let va = a[sortBy] ?? '', vb = b[sortBy] ?? '';
      if (typeof va === 'number') return sortDir === 'asc' ? va - vb : vb - va;
      return sortDir === 'asc' ? String(va).localeCompare(String(vb)) : String(vb).localeCompare(String(va));
    });

    const total = students.length;
    if (pageSize > 0) {
      const start = (page - 1) * pageSize;
      students    = students.slice(start, start + pageSize);
    }

    return { data: students, total, page, pageSize };
  },

  async getStudent(id) {
    await _simulateDelay();
    const s = _load().find(s => s.id === id);
    if (!s) throw new ApiError('Student not found', 404);
    return { data: s };
  },

  async createStudent(payload) {
    await _simulateDelay();
    const students = _load();

    // Duplicate roll number check
    if (students.some(s => s.rollNo.toLowerCase() === payload.rollNo.toLowerCase())) {
      throw new ApiError(`Roll number "${payload.rollNo}" is already registered`, 409);
    }

    const student = {
      id:         _genId(),
      name:       payload.name.trim(),
      rollNo:     payload.rollNo.trim(),
      department: payload.department,
      email:      payload.email.trim(),
      phone:      (payload.phone || '').trim(),
      bloodGroup: (payload.bloodGroup || '').trim(),
      guardianName: (payload.guardianName || '').trim(),
      guardianContact: (payload.guardianContact || '').trim(),
      photo:      payload.photo || null,
      marks:      Number(payload.marks),
      grade:      _grade(Number(payload.marks)),
      joinDate:   payload.joinDate,
      address:    (payload.address || '').trim(),
      createdAt:  Date.now(),
      updatedAt:  Date.now(),
    };
    students.unshift(student);
    _save(students);
    _logActivity('added', student);
    return { data: student };
  },

  async updateStudent(id, payload) {
    await _simulateDelay();
    const students = _load();
    const idx      = students.findIndex(s => s.id === id);
    if (idx === -1) throw new ApiError('Student not found', 404);

    // Duplicate roll number check (exclude self)
    if (students.some(s => s.rollNo.toLowerCase() === payload.rollNo.toLowerCase() && s.id !== id)) {
      throw new ApiError(`Roll number "${payload.rollNo}" is already used by another student`, 409);
    }

    students[idx] = {
      ...students[idx],
      name:       payload.name.trim(),
      rollNo:     payload.rollNo.trim(),
      department: payload.department,
      email:      payload.email.trim(),
      phone:      (payload.phone || '').trim(),
      bloodGroup: (payload.bloodGroup || '').trim(),
      guardianName: (payload.guardianName || '').trim(),
      guardianContact: (payload.guardianContact || '').trim(),
      photo:      payload.photo || null,
      marks:      Number(payload.marks),
      grade:      _grade(Number(payload.marks)),
      joinDate:   payload.joinDate,
      address:    (payload.address || '').trim(),
      updatedAt:  Date.now(),
    };
    _save(students);
    _logActivity('updated', students[idx]);
    return { data: students[idx] };
  },

  async deleteStudent(id) {
    await _simulateDelay();
    const students = _load();
    const idx      = students.findIndex(s => s.id === id);
    if (idx === -1) throw new ApiError('Student not found', 404);
    const [removed] = students.splice(idx, 1);
    _save(students);
    _logActivity('deleted', removed);
    return { data: { id } };
  },

  async getStats() {
    await _simulateDelay();
    const students   = _load();
    const total      = students.length;
    const avgMarks   = total ? Math.round(students.reduce((s, x) => s + x.marks, 0) / total) : 0;
    const departments= [...new Set(students.map(s => s.department))].length;
    const topScorers = students.filter(s => s.grade === 'A+').length;

    const deptMap    = {};
    students.forEach(s => { deptMap[s.department] = (deptMap[s.department] || 0) + 1; });

    return {
      data: {
        total, averageMarks: avgMarks,
        departments, topScorers,
        departmentBreakdown: deptMap,
      }
    };
  },
};

/* ── Activity log (always local, UI only) ── */
function _logActivity(action, student) {
  const log = _getActivityLog();
  log.unshift({ action, name: student.name, dept: student.department, ts: Date.now() });
  localStorage.setItem(ACTIVITY_KEY, JSON.stringify(log.slice(0, 50)));
}
function _getActivityLog() {
  try { return JSON.parse(localStorage.getItem(ACTIVITY_KEY)) || []; } catch { return []; }
}

/* ─────────────────────────────────────────────────────────────
   SECTION 3 — PUBLIC API SERVICE
   These are the functions your pages call.
   They route to MOCK or HTTP depending on the config flag.
───────────────────────────────────────────────────────────── */

const ApiService = {

  /**
   * Get a paginated, filtered, sorted list of students.
   * @param {object} params - { search, department, grade, sortBy, sortDir, page, pageSize }
   * @returns {Promise<{ data: Student[], total: number }>}
   */
  async listStudents(params = {}) {
    if (SMS_CONFIG.USE_MOCK_API) return MOCK.listStudents(params);

    // Build query string for real backend
    const qs = new URLSearchParams();
    if (params.search)     qs.set('search',     params.search);
    if (params.department) qs.set('department', params.department);
    if (params.grade)      qs.set('grade',      params.grade);
    if (params.sortBy)     qs.set('sortBy',     params.sortBy);
    if (params.sortDir)    qs.set('sortDir',    params.sortDir);
    if (params.page)       qs.set('page',       params.page);
    if (params.pageSize)   qs.set('pageSize',   params.pageSize || SMS_CONFIG.PAGE_SIZE);
    const query = qs.toString() ? '?' + qs.toString() : '';

    return httpRequest('GET', `/students${query}`);
  },

  /**
   * Get a single student by ID.
   * @param {string} id
   * @returns {Promise<{ data: Student }>}
   */
  async getStudent(id) {
    if (SMS_CONFIG.USE_MOCK_API) return MOCK.getStudent(id);
    return httpRequest('GET', `/students/${id}`);
  },

  /**
   * Create a new student.
   * @param {object} payload - { name, rollNo, department, email, phone, marks, joinDate, address }
   * @returns {Promise<{ data: Student }>}
   */
  async createStudent(payload) {
    if (SMS_CONFIG.USE_MOCK_API) return MOCK.createStudent(payload);
    return httpRequest('POST', '/students', payload);
  },

  /**
   * Update an existing student.
   * @param {string} id
   * @param {object} payload - same shape as createStudent
   * @returns {Promise<{ data: Student }>}
   */
  async updateStudent(id, payload) {
    if (SMS_CONFIG.USE_MOCK_API) return MOCK.updateStudent(id, payload);
    return httpRequest('PUT', `/students/${id}`, payload);
  },

  /**
   * Delete a student by ID.
   * @param {string} id
   * @returns {Promise<{ data: { id: string } }>}
   */
  async deleteStudent(id) {
    if (SMS_CONFIG.USE_MOCK_API) return MOCK.deleteStudent(id);
    return httpRequest('DELETE', `/students/${id}`);
  },

  /**
   * Get dashboard statistics.
   * @returns {Promise<{ data: Stats }>}
   */
  async getStats() {
    if (SMS_CONFIG.USE_MOCK_API) return MOCK.getStats();
    return httpRequest('GET', '/students/stats');
  },

  /** Expose activity log (always local) */
  getActivityLog: _getActivityLog,

  /** Expose ApiError for instanceof checks in pages */
  ApiError,

  /* ── Feedback Methods ─────────────────────────────────────── */
  listFeedbacks: async function() {
    await _simulateDelay();
    return JSON.parse(localStorage.getItem('sms_feedbacks') || '[]');
  },

  createFeedback: async function(payload) {
    await _simulateDelay();
    const list = JSON.parse(localStorage.getItem('sms_feedbacks') || '[]');
    const id = 'FB-' + Math.floor(1000 + Math.random() * 9000);
    const fb = { ...payload, id, status: 'Pending', timestamp: Date.now() };
    list.unshift(fb);
    localStorage.setItem('sms_feedbacks', JSON.stringify(list));
    return { success: true, data: fb };
  },

  updateFeedbackStatus: async function(id, status) {
    await _simulateDelay();
    const list = JSON.parse(localStorage.getItem('sms_feedbacks') || '[]');
    const idx = list.findIndex(f => f.id === id);
    if (idx !== -1) {
      list[idx].status = status;
      localStorage.setItem('sms_feedbacks', JSON.stringify(list));
    }
    return { success: true };
  },

  deleteFeedback: async function(id) {
    await _simulateDelay();
    let list = JSON.parse(localStorage.getItem('sms_feedbacks') || '[]');
    list = list.filter(f => f.id !== id);
    localStorage.setItem('sms_feedbacks', JSON.stringify(list));
    return { success: true };
  }
};

/* ─────────────────────────────────────────────────────────────
   SECTION 4 — SEED DEMO DATA (mock mode only, first load)
───────────────────────────────────────────────────────────── */
function seedDemoDataIfEmpty() {
  if (!SMS_CONFIG.USE_MOCK_API) return;
  if (_load().length > 0) return;

  const rows = [
    ['Aarav Sharma',    'CS001', 'Computer Science',        'aarav@demo.com',  '9876543210', 92, '2023-07-01'],
    ['Priya Nair',      'MT002', 'Mathematics',             'priya@demo.com',  '9123456789', 78, '2023-07-01'],
    ['Rohan Mehta',     'PH003', 'Physics',                 'rohan@demo.com',  '9988776655', 65, '2023-07-01'],
    ['Sneha Verma',     'CS004', 'Computer Science',        'sneha@demo.com',  '9871234567', 88, '2023-07-15'],
    ['Arnav Singh',     'EN005', 'Engineering',             'arnav@demo.com',  '9900111223', 55, '2023-07-15'],
    ['Diya Patel',      'BI006', 'Biology',                 'diya@demo.com',   '9800000001', 74, '2023-08-01'],
    ['Kabir Joshi',     'BA007', 'Business Administration', 'kabir@demo.com',  '9811111111', 60, '2023-08-01'],
    ['Meera Reddy',     'EC008', 'Economics',               'meera@demo.com',  '9822222222', 83, '2023-08-15'],
    ['Vivaan Gupta',    'CH009', 'Chemistry',               'vivaan@demo.com', '9833333333', 47, '2023-09-01'],
    ['Ananya Kumar',    'LT010', 'Literature',              'ananya@demo.com', '9844444444', 96, '2023-09-01'],
    ['Ishaan Malhotra', 'CS011', 'Computer Science',        'ishaan@demo.com', '9855555555', 71, '2023-09-15'],
    ['Tanvi Agarwal',   'PS012', 'Psychology',              'tanvi@demo.com',  '9866666666', 85, '2023-09-15'],
  ];

  const students = rows.map(([n, r, d, e, p, m, j]) => ({
    id: _genId(), name: n, rollNo: r, department: d, email: e, phone: p,
    marks: m, grade: _grade(m), joinDate: j, address: '',
    createdAt: Date.now(), updatedAt: Date.now(),
  }));
  _save(students);

  // Seed feedback
  if (!localStorage.getItem('sms_feedbacks')) {
    localStorage.setItem('sms_feedbacks', JSON.stringify([
      { id: 'FB-1001', studentName: 'Aarav Sharma', subject: 'Lab Computers Issue', category: 'Facilities', message: 'The computers in Lab 3 randomly restart during compilation. Please check the power supply.', status: 'Pending', timestamp: Date.now() - 86400000 },
      { id: 'FB-1002', studentName: 'Diya Patel', subject: 'More Reference Books', category: 'Library', message: 'Could we get more copies of the recommended biology textbooks? They are always checked out.', status: 'Resolved', timestamp: Date.now() - 345600000 },
      { id: 'FB-1003', studentName: 'Ananya Kumar', subject: 'Seminar Schedule Clash', category: 'Academic', message: 'The literature seminar clashes with the guest lecture tomorrow. Can it be rescheduled?', status: 'Pending', timestamp: Date.now() - 1200000 },
    ]));
  }
}

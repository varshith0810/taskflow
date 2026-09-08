const BASE = import.meta.env.VITE_API_URL || '';

function getToken() {
  return localStorage.getItem('access_token');
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...options.headers };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${BASE}/api/v1${path}`, { ...options, headers });

  if (res.status === 401) {
    // Try refresh
    const refreshed = await tryRefresh();
    if (refreshed) {
      headers['Authorization'] = `Bearer ${getToken()}`;
      const retry = await fetch(`${BASE}/api/v1${path}`, { ...options, headers });
      if (!retry.ok) {
        const err = await retry.json().catch(() => ({}));
        throw new Error(err.detail || `HTTP ${retry.status}`);
      }
      return retry.status === 204 ? null : retry.json();
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.dispatchEvent(new Event('auth:logout'));
      throw new Error('Session expired');
    }
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }

  return res.status === 204 ? null : res.json();
}

async function tryRefresh() {
  const refresh = localStorage.getItem('refresh_token');
  if (!refresh) return false;
  try {
    const res = await fetch(`${BASE}/api/v1/auth/refresh`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

// Auth
export const auth = {
  signup: (data) => request('/auth/signup', { method: 'POST', body: JSON.stringify(data) }),
  login: async (data) => {
    const res = await request('/auth/login', { method: 'POST', body: JSON.stringify(data) });
    localStorage.setItem('access_token', res.access_token);
    localStorage.setItem('refresh_token', res.refresh_token);
    return res;
  },
  me: () => request('/auth/me'),
  updateMe: (data) => request('/auth/me', { method: 'PATCH', body: JSON.stringify(data) }),
  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
};

// Users
export const users = {
  search: (q = '') => request(`/users/search?q=${encodeURIComponent(q)}`),
  organization: () => request('/users/organization'),
};

// Projects
export const projects = {
  list: (skip = 0, limit = 50) => request(`/projects?skip=${skip}&limit=${limit}`),
  create: (data) => request('/projects', { method: 'POST', body: JSON.stringify(data) }),
  get: (id) => request(`/projects/${id}`),
  update: (id, data) => request(`/projects/${id}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (id) => request(`/projects/${id}`, { method: 'DELETE' }),
  listMembers: (id) => request(`/projects/${id}/members`),
  addMember: (id, data) => request(`/projects/${id}/members`, { method: 'POST', body: JSON.stringify(data) }),
  updateMember: (id, uid, data) => request(`/projects/${id}/members/${uid}`, { method: 'PATCH', body: JSON.stringify(data) }),
  removeMember: (id, uid) => request(`/projects/${id}/members/${uid}`, { method: 'DELETE' }),
};

// Tasks
export const tasks = {
  list: (projectId, params = {}) => {
    const q = new URLSearchParams();
    if (params.status) q.set('status', params.status);
    if (params.assignee_id) q.set('assignee_id', params.assignee_id);
    if (params.overdue_only) q.set('overdue_only', 'true');
    if (params.skip) q.set('skip', params.skip);
    if (params.limit) q.set('limit', params.limit);
    return request(`/projects/${projectId}/tasks?${q}`);
  },
  create: (projectId, data) => request(`/projects/${projectId}/tasks`, { method: 'POST', body: JSON.stringify(data) }),
  get: (projectId, taskId) => request(`/projects/${projectId}/tasks/${taskId}`),
  update: (projectId, taskId, data) => request(`/projects/${projectId}/tasks/${taskId}`, { method: 'PATCH', body: JSON.stringify(data) }),
  delete: (projectId, taskId) => request(`/projects/${projectId}/tasks/${taskId}`, { method: 'DELETE' }),
};

// Dashboard
export const dashboard = {
  get: () => request('/dashboard'),
};

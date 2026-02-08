/**
 * MeetingMind API Client
 * Handles all HTTP communication with the backend API.
 */

const BASE_URL = '/api';

async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  };

  if (config.body && typeof config.body === 'object') {
    config.body = JSON.stringify(config.body);
  }

  const response = await fetch(url, config);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  if (response.status === 204) return null;
  return response.json();
}

// --- Meetings ---

export async function getMeetings(params = {}) {
  const query = new URLSearchParams();
  if (params.status) query.set('status', params.status);
  if (params.search) query.set('search', params.search);
  if (params.skip) query.set('skip', params.skip);
  if (params.limit) query.set('limit', params.limit);
  const qs = query.toString();
  return request(`/meetings${qs ? '?' + qs : ''}`);
}

export async function getMeeting(id) {
  return request(`/meetings/${id}`);
}

export async function createMeeting(data) {
  return request('/meetings', { method: 'POST', body: data });
}

export async function updateMeeting(id, data) {
  return request(`/meetings/${id}`, { method: 'PUT', body: data });
}

export async function deleteMeeting(id) {
  return request(`/meetings/${id}`, { method: 'DELETE' });
}

export async function uploadTranscript(meetingId, transcript) {
  return request(`/meetings/${meetingId}/transcript`, {
    method: 'POST',
    body: { transcript },
  });
}

export async function processMeeting(meetingId) {
  return request(`/meetings/${meetingId}/process`, { method: 'POST' });
}

// --- Action Items ---

export async function getActionItems(params = {}) {
  const query = new URLSearchParams();
  if (params.meeting_id) query.set('meeting_id', params.meeting_id);
  if (params.status) query.set('status', params.status);
  if (params.priority) query.set('priority', params.priority);
  if (params.assignee) query.set('assignee', params.assignee);
  const qs = query.toString();
  return request(`/action-items${qs ? '?' + qs : ''}`);
}

export async function updateActionItem(id, data) {
  return request(`/action-items/${id}`, { method: 'PUT', body: data });
}

export async function deleteActionItem(id) {
  return request(`/action-items/${id}`, { method: 'DELETE' });
}

// --- Integrations ---

export async function getIntegrations() {
  return request('/integrations');
}

export async function updateIntegration(serviceName, data) {
  return request(`/integrations/${serviceName}`, { method: 'PUT', body: data });
}

export async function testIntegration(serviceName) {
  return request(`/integrations/${serviceName}/test`, { method: 'POST' });
}

// --- Analytics ---

export async function getDashboardStats() {
  return request('/analytics/dashboard');
}

export async function getMeetingsOverTime(days = 30) {
  return request(`/analytics/meetings-over-time?days=${days}`);
}

export async function getActionItemSummary() {
  return request('/analytics/action-item-summary');
}

// --- Health ---

export async function getHealth() {
  return request('/health');
}

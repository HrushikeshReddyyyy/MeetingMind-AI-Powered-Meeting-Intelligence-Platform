import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getMeetings, createMeeting, deleteMeeting } from '../api';

function Meetings() {
  const [meetings, setMeetings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    date: '',
    duration_minutes: '',
    participants: '',
  });

  useEffect(() => {
    loadMeetings();
  }, [statusFilter, searchQuery]);

  async function loadMeetings() {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (searchQuery) params.search = searchQuery;
      const data = await getMeetings(params);
      setMeetings(data);
    } catch (err) {
      console.error('Failed to load meetings:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    try {
      const payload = {
        title: formData.title,
        date: formData.date ? new Date(formData.date).toISOString() : undefined,
        duration_minutes: formData.duration_minutes ? parseInt(formData.duration_minutes) : undefined,
        participants: formData.participants ? formData.participants.split(',').map(p => p.trim()).filter(Boolean) : undefined,
      };
      await createMeeting(payload);
      setShowModal(false);
      setFormData({ title: '', date: '', duration_minutes: '', participants: '' });
      loadMeetings();
    } catch (err) {
      alert('Failed to create meeting: ' + err.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm('Are you sure you want to delete this meeting?')) return;
    try {
      await deleteMeeting(id);
      loadMeetings();
    } catch (err) {
      alert('Failed to delete meeting: ' + err.message);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Meetings</h2>
          <p>Manage and process your meeting recordings</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowModal(true)}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Meeting
        </button>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 16, padding: 16 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <input
            type="text"
            className="form-input"
            placeholder="Search meetings..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            style={{ maxWidth: 300 }}
          />
          <select
            className="form-select"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            style={{ maxWidth: 200 }}
          >
            <option value="">All Statuses</option>
            <option value="scheduled">Scheduled</option>
            <option value="recording">Recording</option>
            <option value="transcribing">Transcribing</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>

      {/* Meetings Table */}
      <div className="card">
        {loading ? (
          <div className="loading"><div className="spinner" /> Loading meetings...</div>
        ) : meetings.length === 0 ? (
          <div className="empty-state">
            <h3>No meetings found</h3>
            <p>Create a new meeting or adjust your filters.</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Create Meeting</button>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Date</th>
                  <th>Duration</th>
                  <th>Participants</th>
                  <th>Status</th>
                  <th>Actions</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {meetings.map(m => (
                  <tr key={m.id}>
                    <td><Link to={`/meetings/${m.id}`} style={{ fontWeight: 500 }}>{m.title}</Link></td>
                    <td>{m.date ? new Date(m.date).toLocaleDateString() : '-'}</td>
                    <td>{m.duration_minutes ? `${m.duration_minutes} min` : '-'}</td>
                    <td>{m.participants ? m.participants.length : 0}</td>
                    <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                    <td>{m.action_item_count} items</td>
                    <td>
                      <button className="btn-icon" onClick={() => handleDelete(m.id)} title="Delete">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Create Meeting Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Meeting</h3>
              <button className="btn-icon" onClick={() => setShowModal(false)}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-group">
                <label>Meeting Title *</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.title}
                  onChange={e => setFormData({ ...formData, title: e.target.value })}
                  placeholder="e.g., Weekly Team Standup"
                  required
                />
              </div>
              <div className="form-group">
                <label>Date</label>
                <input
                  type="datetime-local"
                  className="form-input"
                  value={formData.date}
                  onChange={e => setFormData({ ...formData, date: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label>Duration (minutes)</label>
                <input
                  type="number"
                  className="form-input"
                  value={formData.duration_minutes}
                  onChange={e => setFormData({ ...formData, duration_minutes: e.target.value })}
                  placeholder="e.g., 60"
                  min="1"
                />
              </div>
              <div className="form-group">
                <label>Participants (comma-separated)</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.participants}
                  onChange={e => setFormData({ ...formData, participants: e.target.value })}
                  placeholder="e.g., John, Jane, Bob"
                />
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary">Create Meeting</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default Meetings;

import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getActionItems, updateActionItem, deleteActionItem } from '../api';

function ActionItems() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');

  useEffect(() => {
    loadItems();
  }, [statusFilter, priorityFilter]);

  async function loadItems() {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter) params.status = statusFilter;
      if (priorityFilter) params.priority = priorityFilter;
      const data = await getActionItems(params);
      setItems(data);
    } catch (err) {
      console.error('Failed to load action items:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleStatusChange(itemId, newStatus) {
    try {
      await updateActionItem(itemId, { status: newStatus });
      loadItems();
    } catch (err) {
      alert('Failed to update: ' + err.message);
    }
  }

  async function handleDelete(itemId) {
    if (!confirm('Delete this action item?')) return;
    try {
      await deleteActionItem(itemId);
      loadItems();
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Action Items</h2>
          <p>Track and manage action items from all meetings</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ marginBottom: 16, padding: 16 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
          <select
            className="form-select"
            value={statusFilter}
            onChange={e => setStatusFilter(e.target.value)}
            style={{ maxWidth: 200 }}
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="overdue">Overdue</option>
          </select>
          <select
            className="form-select"
            value={priorityFilter}
            onChange={e => setPriorityFilter(e.target.value)}
            style={{ maxWidth: 200 }}
          >
            <option value="">All Priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <span style={{ fontSize: 13, color: 'var(--color-text-secondary)' }}>
            {items.length} item{items.length !== 1 ? 's' : ''}
          </span>
        </div>
      </div>

      {/* Items Table */}
      <div className="card">
        {loading ? (
          <div className="loading"><div className="spinner" /> Loading action items...</div>
        ) : items.length === 0 ? (
          <div className="empty-state">
            <h3>No action items</h3>
            <p>Action items are automatically extracted when you process a meeting transcript.</p>
            <Link to="/meetings" className="btn btn-primary">Go to Meetings</Link>
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th style={{ width: 40 }}></th>
                  <th>Description</th>
                  <th>Assignee</th>
                  <th>Priority</th>
                  <th>Due Date</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map(item => (
                  <tr key={item.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={item.status === 'completed'}
                        onChange={() =>
                          handleStatusChange(item.id, item.status === 'completed' ? 'pending' : 'completed')
                        }
                        style={{ cursor: 'pointer', width: 18, height: 18 }}
                      />
                    </td>
                    <td style={{ textDecoration: item.status === 'completed' ? 'line-through' : 'none' }}>
                      {item.description}
                    </td>
                    <td>{item.assignee || 'Unassigned'}</td>
                    <td><span className={`badge badge-${item.priority}`}>{item.priority}</span></td>
                    <td>{item.due_date ? new Date(item.due_date).toLocaleDateString() : '-'}</td>
                    <td>
                      <select
                        value={item.status}
                        onChange={e => handleStatusChange(item.id, e.target.value)}
                        className="form-select"
                        style={{ padding: '4px 8px', fontSize: 12, width: 'auto' }}
                      >
                        <option value="pending">Pending</option>
                        <option value="in_progress">In Progress</option>
                        <option value="completed">Completed</option>
                        <option value="overdue">Overdue</option>
                      </select>
                    </td>
                    <td>
                      <button className="btn-icon" onClick={() => handleDelete(item.id)} title="Delete">
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
    </div>
  );
}

export default ActionItems;

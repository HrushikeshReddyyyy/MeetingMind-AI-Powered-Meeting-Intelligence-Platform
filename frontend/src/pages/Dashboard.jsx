import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getDashboardStats, getMeetings, getActionItems } from '../api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [recentMeetings, setRecentMeetings] = useState([]);
  const [pendingItems, setPendingItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const [statsData, meetingsData, itemsData] = await Promise.all([
        getDashboardStats(),
        getMeetings({ limit: 5 }),
        getActionItems({ status: 'pending', limit: 5 }),
      ]);
      setStats(statsData);
      setRecentMeetings(meetingsData);
      setPendingItems(itemsData);
    } catch (err) {
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading dashboard...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Dashboard</h2>
          <p>Overview of your meeting intelligence platform</p>
        </div>
        <Link to="/meetings" className="btn btn-primary">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New Meeting
        </Link>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-label">Total Meetings</div>
          <div className="stat-value">{stats?.total_meetings || 0}</div>
          <div className="stat-sub">{stats?.meetings_this_week || 0} this week</div>
        </div>
        <div className="stat-card success">
          <div className="stat-label">Completed</div>
          <div className="stat-value">{stats?.completed_meetings || 0}</div>
          <div className="stat-sub">meetings processed</div>
        </div>
        <div className="stat-card info">
          <div className="stat-label">Action Items</div>
          <div className="stat-value">{stats?.total_action_items || 0}</div>
          <div className="stat-sub">{stats?.pending_action_items || 0} pending</div>
        </div>
        <div className="stat-card danger">
          <div className="stat-label">Completion Rate</div>
          <div className="stat-value">{stats?.action_completion_rate || 0}%</div>
          <div className="stat-sub">{stats?.overdue_action_items || 0} overdue items</div>
        </div>
      </div>

      <div className="grid-2">
        {/* Recent Meetings */}
        <div className="card">
          <div className="card-header">
            <h3>Recent Meetings</h3>
            <Link to="/meetings" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          {recentMeetings.length === 0 ? (
            <div className="empty-state">
              <p>No meetings yet. Create your first meeting to get started.</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Title</th>
                    <th>Status</th>
                    <th>Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentMeetings.map(m => (
                    <tr key={m.id}>
                      <td><Link to={`/meetings/${m.id}`}>{m.title}</Link></td>
                      <td><span className={`badge badge-${m.status}`}>{m.status}</span></td>
                      <td>{m.date ? new Date(m.date).toLocaleDateString() : '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pending Action Items */}
        <div className="card">
          <div className="card-header">
            <h3>Pending Action Items</h3>
            <Link to="/action-items" className="btn btn-sm btn-secondary">View All</Link>
          </div>
          {pendingItems.length === 0 ? (
            <div className="empty-state">
              <p>No pending action items. Process a meeting to extract action items.</p>
            </div>
          ) : (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Priority</th>
                    <th>Assignee</th>
                  </tr>
                </thead>
                <tbody>
                  {pendingItems.map(item => (
                    <tr key={item.id}>
                      <td>{item.description.length > 60 ? item.description.substring(0, 60) + '...' : item.description}</td>
                      <td><span className={`badge badge-${item.priority}`}>{item.priority}</span></td>
                      <td>{item.assignee || 'Unassigned'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

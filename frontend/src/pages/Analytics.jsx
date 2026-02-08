import React, { useState, useEffect } from 'react';
import { getDashboardStats, getMeetingsOverTime, getActionItemSummary } from '../api';

function Analytics() {
  const [stats, setStats] = useState(null);
  const [meetingsTimeline, setMeetingsTimeline] = useState([]);
  const [actionSummary, setActionSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  async function loadAnalytics() {
    try {
      const [statsData, timelineData, summaryData] = await Promise.all([
        getDashboardStats(),
        getMeetingsOverTime(30),
        getActionItemSummary(),
      ]);
      setStats(statsData);
      setMeetingsTimeline(timelineData);
      setActionSummary(summaryData);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading analytics...</div>;
  }

  const maxCount = Math.max(...meetingsTimeline.map(d => d.count), 1);

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Analytics</h2>
          <p>Meeting intelligence insights and trends</p>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="stats-grid">
        <div className="stat-card primary">
          <div className="stat-label">Total Meetings</div>
          <div className="stat-value">{stats?.total_meetings || 0}</div>
        </div>
        <div className="stat-card success">
          <div className="stat-label">Avg Duration</div>
          <div className="stat-value">{stats?.avg_meeting_duration ? `${Math.round(stats.avg_meeting_duration)}m` : 'N/A'}</div>
        </div>
        <div className="stat-card info">
          <div className="stat-label">Action Completion</div>
          <div className="stat-value">{stats?.action_completion_rate || 0}%</div>
        </div>
        <div className="stat-card danger">
          <div className="stat-label">Overdue Items</div>
          <div className="stat-value">{stats?.overdue_action_items || 0}</div>
        </div>
      </div>

      <div className="grid-2">
        {/* Meetings Over Time Chart */}
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Meetings Over Time (30 days)</h3>
          {meetingsTimeline.length === 0 ? (
            <div className="empty-state"><p>No meeting data available yet.</p></div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'flex-end', gap: 4, height: 160, padding: '0 8px' }}>
              {meetingsTimeline.map((d, i) => (
                <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div
                    style={{
                      width: '100%',
                      maxWidth: 40,
                      height: `${(d.count / maxCount) * 140}px`,
                      minHeight: 4,
                      background: 'var(--color-primary)',
                      borderRadius: '4px 4px 0 0',
                      transition: 'height 0.3s ease',
                    }}
                    title={`${d.date}: ${d.count} meeting(s)`}
                  />
                  {i % Math.ceil(meetingsTimeline.length / 7) === 0 && (
                    <span style={{ fontSize: 10, color: 'var(--color-text-muted)', marginTop: 4 }}>
                      {new Date(d.date).toLocaleDateString('en', { month: 'short', day: 'numeric' })}
                    </span>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Action Items Breakdown */}
        <div className="card">
          <h3 style={{ marginBottom: 16 }}>Action Items Breakdown</h3>
          {!actionSummary ? (
            <div className="empty-state"><p>No action item data available.</p></div>
          ) : (
            <div>
              <h4 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 12 }}>
                By Status
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 24 }}>
                {Object.entries(actionSummary.by_status || {}).map(([status, count]) => (
                  <div key={status} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 90, fontSize: 13, textTransform: 'capitalize' }}>{status.replace('_', ' ')}</span>
                    <div style={{ flex: 1, height: 24, background: 'var(--color-bg)', borderRadius: 4, overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${(count / Math.max(stats?.total_action_items || 1, 1)) * 100}%`,
                          background: status === 'completed' ? 'var(--color-success)' :
                                     status === 'overdue' ? 'var(--color-danger)' :
                                     status === 'in_progress' ? 'var(--color-warning)' : 'var(--color-info)',
                          borderRadius: 4,
                          transition: 'width 0.3s ease',
                        }}
                      />
                    </div>
                    <span style={{ fontSize: 13, fontWeight: 600, width: 30, textAlign: 'right' }}>{count}</span>
                  </div>
                ))}
              </div>

              <h4 style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-secondary)', marginBottom: 12 }}>
                By Priority
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {Object.entries(actionSummary.by_priority || {}).map(([priority, count]) => (
                  <div key={priority} style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <span style={{ width: 90, fontSize: 13, textTransform: 'capitalize' }}>{priority}</span>
                    <div style={{ flex: 1, height: 24, background: 'var(--color-bg)', borderRadius: 4, overflow: 'hidden' }}>
                      <div
                        style={{
                          height: '100%',
                          width: `${(count / Math.max(stats?.total_action_items || 1, 1)) * 100}%`,
                          background: priority === 'high' ? 'var(--color-danger)' :
                                     priority === 'medium' ? 'var(--color-warning)' : 'var(--color-success)',
                          borderRadius: 4,
                          transition: 'width 0.3s ease',
                        }}
                      />
                    </div>
                    <span style={{ fontSize: 13, fontWeight: 600, width: 30, textAlign: 'right' }}>{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Platform Impact */}
      <div className="card" style={{ marginTop: 24 }}>
        <h3 style={{ marginBottom: 16 }}>Platform Impact</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-label">Time Saved (estimated)</div>
            <div className="stat-value">{Math.round((stats?.completed_meetings || 0) * 0.5)}h</div>
            <div className="stat-sub">~30 min per meeting on notes & follow-ups</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Documentation Rate</div>
            <div className="stat-value">
              {stats?.total_meetings ? Math.round((stats.completed_meetings / stats.total_meetings) * 100) : 0}%
            </div>
            <div className="stat-sub">meetings fully documented</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">Action Item Tracking</div>
            <div className="stat-value">{stats?.total_action_items || 0}</div>
            <div className="stat-sub">items tracked across all meetings</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Analytics;

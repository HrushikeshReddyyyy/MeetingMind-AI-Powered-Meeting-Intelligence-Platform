import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getMeeting, uploadTranscript, processMeeting, updateActionItem } from '../api';

function MeetingDetail() {
  const { id } = useParams();
  const [meeting, setMeeting] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transcript, setTranscript] = useState('');
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  const pollRef = useRef(null);

  useEffect(() => {
    loadMeeting();
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, [id]);

  async function loadMeeting() {
    try {
      setError(null);
      const data = await getMeeting(id);
      setMeeting(data);
    } catch (err) {
      setError('Failed to load meeting. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  }

  async function handleUploadTranscript() {
    if (!transcript.trim()) return;
    try {
      setUploading(true);
      await uploadTranscript(id, transcript);
      setTranscript('');
      pollMeetingStatus();
    } catch (err) {
      alert('Failed to upload transcript: ' + err.message);
    } finally {
      setUploading(false);
    }
  }

  async function handleProcess() {
    try {
      setProcessing(true);
      await processMeeting(id);
      pollMeetingStatus();
    } catch (err) {
      alert('Failed to process meeting: ' + err.message);
    } finally {
      setProcessing(false);
    }
  }

  function pollMeetingStatus() {
    if (pollRef.current) clearInterval(pollRef.current);
    let attempts = 0;
    pollRef.current = setInterval(async () => {
      attempts++;
      try {
        const data = await getMeeting(id);
        setMeeting(data);
        if (data.status === 'completed' || data.status === 'failed' || attempts > 30) {
          clearInterval(pollRef.current);
          pollRef.current = null;
        }
      } catch {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    }, 2000);
  }

  async function handleToggleActionItem(itemId, currentStatus) {
    const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
    try {
      await updateActionItem(itemId, { status: newStatus });
      loadMeeting();
    } catch (err) {
      alert('Failed to update action item: ' + err.message);
    }
  }

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading meeting...</div>;
  }

  if (error) {
    return (
      <div className="empty-state">
        <h3>Something went wrong</h3>
        <p>{error}</p>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', marginTop: 12 }}>
          <button className="btn btn-primary" onClick={() => { setLoading(true); loadMeeting(); }}>Retry</button>
          <Link to="/meetings" className="btn btn-secondary">Back to Meetings</Link>
        </div>
      </div>
    );
  }

  if (!meeting) {
    return (
      <div className="empty-state">
        <h3>Meeting not found</h3>
        <Link to="/meetings" className="btn btn-primary">Back to Meetings</Link>
      </div>
    );
  }

  const topicTags = meeting.analytics?.topic_tags || [];

  return (
    <div>
      <div className="page-header">
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 4 }}>
            <Link to="/meetings" style={{ color: 'var(--color-text-secondary)' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6"/></svg>
            </Link>
            <h2>{meeting.title}</h2>
            <span className={`badge badge-${meeting.status}`}>{meeting.status}</span>
          </div>
          <p style={{ marginLeft: 32 }}>
            {meeting.date ? new Date(meeting.date).toLocaleString() : 'No date set'}
            {meeting.duration_minutes ? ` | ${meeting.duration_minutes} min` : ''}
            {meeting.participants ? ` | ${meeting.participants.join(', ')}` : ''}
          </p>
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          {meeting.transcript && meeting.status !== 'completed' && meeting.status !== 'processing' && meeting.status !== 'transcribing' && (
            <button className="btn btn-primary" onClick={handleProcess} disabled={processing}>
              {processing ? 'Processing...' : 'Process Meeting'}
            </button>
          )}
          {meeting.synced_to_notion && (
            <span className="badge badge-connected" style={{ padding: '6px 12px' }}>Synced to Notion</span>
          )}
        </div>
      </div>

      {/* Upload Transcript */}
      {!meeting.transcript && (
        <div className="card" style={{ marginBottom: 24 }}>
          <h3 style={{ marginBottom: 12 }}>Upload Transcript</h3>
          <p style={{ fontSize: 14, color: 'var(--color-text-secondary)', marginBottom: 12 }}>
            Paste a meeting transcript below to generate AI-powered summaries, action items, and analytics.
          </p>
          <textarea
            className="form-textarea"
            value={transcript}
            onChange={e => setTranscript(e.target.value)}
            placeholder={"Paste your meeting transcript here...\n\nExample:\nJohn: Let's discuss the Q4 roadmap.\nJane: I think we should prioritize the mobile app.\nBob: Agreed. We need to finalize the design by next Friday."}
            style={{ minHeight: 200 }}
          />
          <div style={{ marginTop: 12, display: 'flex', gap: 8 }}>
            <button
              className="btn btn-primary"
              onClick={handleUploadTranscript}
              disabled={!transcript.trim() || uploading}
            >
              {uploading ? 'Uploading...' : 'Upload & Process'}
            </button>
          </div>
        </div>
      )}

      {/* Processing indicator */}
      {(meeting.status === 'processing' || meeting.status === 'transcribing') && (
        <div className="card" style={{ marginBottom: 24, textAlign: 'center', padding: 32 }}>
          <div className="spinner" style={{ margin: '0 auto 12px' }} />
          <h3>Processing meeting...</h3>
          <p style={{ color: 'var(--color-text-secondary)' }}>
            Generating summary, extracting action items, and analyzing content.
          </p>
        </div>
      )}

      {/* Content Tabs */}
      {meeting.status === 'completed' && (
        <>
          <div style={{ display: 'flex', gap: 4, marginBottom: 16, borderBottom: '2px solid var(--color-border)', paddingBottom: 0 }}>
            {['summary', 'action-items', 'transcript', 'analytics'].map(tab => (
              <button
                key={tab}
                className="btn"
                onClick={() => setActiveTab(tab)}
                style={{
                  borderRadius: '8px 8px 0 0',
                  borderBottom: activeTab === tab ? '2px solid var(--color-primary)' : '2px solid transparent',
                  fontWeight: activeTab === tab ? 600 : 400,
                  color: activeTab === tab ? 'var(--color-primary-dark)' : 'var(--color-text-secondary)',
                  background: activeTab === tab ? 'var(--color-primary-bg)' : 'transparent',
                  marginBottom: -2,
                }}
              >
                {tab.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
              </button>
            ))}
          </div>

          {activeTab === 'summary' && (
            <div className="card">
              <div className="detail-section">
                <h3>Meeting Summary</h3>
                <div className="content">{meeting.summary || 'No summary available.'}</div>
              </div>
              {meeting.key_decisions && meeting.key_decisions.length > 0 && (
                <div className="detail-section">
                  <h3>Key Decisions</h3>
                  <ul className="decision-list">
                    {meeting.key_decisions.map((decision) => (
                      <li key={decision}>{decision}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {activeTab === 'action-items' && (
            <div className="card">
              <div className="card-header">
                <h3>Action Items ({meeting.action_items?.length || 0})</h3>
              </div>
              {!meeting.action_items || meeting.action_items.length === 0 ? (
                <div className="empty-state"><p>No action items extracted.</p></div>
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
                      </tr>
                    </thead>
                    <tbody>
                      {meeting.action_items.map(item => (
                        <tr key={item.id}>
                          <td>
                            <input
                              type="checkbox"
                              checked={item.status === 'completed'}
                              onChange={() => handleToggleActionItem(item.id, item.status)}
                              style={{ cursor: 'pointer', width: 18, height: 18 }}
                            />
                          </td>
                          <td style={{ textDecoration: item.status === 'completed' ? 'line-through' : 'none' }}>
                            {item.description}
                          </td>
                          <td>{item.assignee || 'Unassigned'}</td>
                          <td><span className={`badge badge-${item.priority}`}>{item.priority}</span></td>
                          <td>{item.due_date ? new Date(item.due_date).toLocaleDateString() : '-'}</td>
                          <td><span className={`badge badge-${item.status}`}>{item.status}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}

          {activeTab === 'transcript' && (
            <div className="card">
              <div className="detail-section">
                <h3>Full Transcript</h3>
                <div className="content">{meeting.transcript || 'No transcript available.'}</div>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && meeting.analytics && (
            <div className="card">
              <h3 style={{ marginBottom: 16 }}>Meeting Analytics</h3>
              <div className="stats-grid">
                <div className="stat-card primary">
                  <div className="stat-label">Word Count</div>
                  <div className="stat-value">{meeting.analytics.word_count}</div>
                </div>
                <div className="stat-card info">
                  <div className="stat-label">Speakers</div>
                  <div className="stat-value">{meeting.analytics.speaker_count}</div>
                </div>
                <div className="stat-card success">
                  <div className="stat-label">Sentiment</div>
                  <div className="stat-value" style={{ fontSize: 22, textTransform: 'capitalize' }}>
                    {meeting.analytics.sentiment_score || 'N/A'}
                  </div>
                </div>
                <div className="stat-card">
                  <div className="stat-label">Engagement Score</div>
                  <div className="stat-value">{meeting.analytics.engagement_score || 'N/A'}</div>
                  <div className="stat-sub">out of 100</div>
                </div>
              </div>
              {topicTags.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <h4 style={{ fontSize: 14, fontWeight: 600, marginBottom: 8 }}>Topics</h4>
                  <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                    {topicTags.map((tag) => (
                      <span key={tag} className="badge badge-processing" style={{ padding: '4px 12px' }}>{tag}</span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default MeetingDetail;

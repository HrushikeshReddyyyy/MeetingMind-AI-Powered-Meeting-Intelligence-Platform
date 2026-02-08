import React, { useState, useEffect } from 'react';
import { getIntegrations, updateIntegration, testIntegration } from '../api';

const SERVICE_INFO = {
  otter: {
    name: 'Otter.ai',
    description: 'AI-powered meeting transcription service. Automatically transcribes meetings and syncs transcripts.',
    icon: '🎙',
  },
  notion: {
    name: 'Notion',
    description: 'Workspace for meeting documentation. Automatically creates pages with summaries and action items.',
    icon: '📝',
  },
  zapier: {
    name: 'Zapier',
    description: 'Workflow automation for distributing summaries, assigning action items, and sending follow-up reminders.',
    icon: '⚡',
  },
  openai: {
    name: 'OpenAI',
    description: 'AI engine for generating meeting summaries, extracting action items, and analyzing sentiment.',
    icon: '🤖',
  },
};

function Settings() {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [testing, setTesting] = useState({});

  useEffect(() => {
    loadIntegrations();
  }, []);

  async function loadIntegrations() {
    try {
      const data = await getIntegrations();
      setIntegrations(data);
    } catch (err) {
      console.error('Failed to load integrations:', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleToggle(serviceName, currentEnabled) {
    try {
      await updateIntegration(serviceName, { is_enabled: !currentEnabled });
      loadIntegrations();
    } catch (err) {
      alert('Failed to update: ' + err.message);
    }
  }

  async function handleTest(serviceName) {
    try {
      setTesting(prev => ({ ...prev, [serviceName]: true }));
      const result = await testIntegration(serviceName);
      alert(`${SERVICE_INFO[serviceName].name}: ${result.message}`);
      loadIntegrations();
    } catch (err) {
      alert('Connection test failed: ' + err.message);
    } finally {
      setTesting(prev => ({ ...prev, [serviceName]: false }));
    }
  }

  if (loading) {
    return <div className="loading"><div className="spinner" /> Loading settings...</div>;
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <h2>Settings</h2>
          <p>Configure integrations and platform settings</p>
        </div>
      </div>

      {/* Integration Cards */}
      <div className="integration-grid">
        {integrations.map(config => {
          const info = SERVICE_INFO[config.service_name] || { name: config.service_name, description: '', icon: '🔌' };
          return (
            <div className="integration-card" key={config.id}>
              <div className="integration-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 24 }}>{info.icon}</span>
                  <div>
                    <h3>{info.name}</h3>
                    <span className={`badge badge-${config.status}`}>{config.status}</span>
                  </div>
                </div>
                <label className="toggle">
                  <input
                    type="checkbox"
                    checked={config.is_enabled}
                    onChange={() => handleToggle(config.service_name, config.is_enabled)}
                  />
                  <span className="toggle-slider" />
                </label>
              </div>
              <p>{info.description}</p>
              {config.last_sync && (
                <p style={{ fontSize: 12, color: 'var(--color-text-muted)', marginBottom: 12 }}>
                  Last tested: {new Date(config.last_sync).toLocaleString()}
                </p>
              )}
              <div className="integration-actions">
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => handleTest(config.service_name)}
                  disabled={testing[config.service_name]}
                >
                  {testing[config.service_name] ? 'Testing...' : 'Test Connection'}
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Configuration Guide */}
      <div className="card" style={{ marginTop: 24 }}>
        <h3 style={{ marginBottom: 16 }}>Setup Guide</h3>
        <div style={{ fontSize: 14, lineHeight: 1.8, color: 'var(--color-text-secondary)' }}>
          <p><strong>1. Otter.ai</strong> - Set <code>OTTER_EMAIL</code> and <code>OTTER_PASSWORD</code> in your <code>.env</code> file to enable automatic transcription.</p>
          <p><strong>2. Notion</strong> - Create a Notion integration at developers.notion.com, then set <code>NOTION_API_KEY</code> and <code>NOTION_DATABASE_ID</code> in your <code>.env</code> file.</p>
          <p><strong>3. Zapier</strong> - Create Zaps with webhook triggers, then set the webhook URLs (<code>ZAPIER_WEBHOOK_SUMMARY</code>, <code>ZAPIER_WEBHOOK_ACTION_ITEMS</code>, <code>ZAPIER_WEBHOOK_FOLLOWUP</code>) in your <code>.env</code> file.</p>
          <p><strong>4. OpenAI</strong> - Get an API key from platform.openai.com and set <code>OPENAI_API_KEY</code> in your <code>.env</code> file.</p>
        </div>
      </div>
    </div>
  );
}

export default Settings;

import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import App from '../App';

// Mock the fetch API
global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve([]),
  })
);

describe('App', () => {
  it('renders the sidebar with MeetingMind branding', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByText('MeetingMind')).toBeInTheDocument();
    expect(screen.getByText('AI Meeting Intelligence')).toBeInTheDocument();
  });

  it('renders all navigation links', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Meetings')).toBeInTheDocument();
    expect(screen.getByText('Action Items')).toBeInTheDocument();
    expect(screen.getByText('Analytics')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('renders dashboard by default', () => {
    render(
      <MemoryRouter initialEntries={['/dashboard']}>
        <App />
      </MemoryRouter>
    );
    // Dashboard should show loading or content
    expect(document.querySelector('.main-content')).toBeInTheDocument();
  });
});

import { describe, it, expect, vi, beforeEach } from 'vitest';

// We test the API module by mocking fetch
beforeEach(() => {
  global.fetch = vi.fn();
});

describe('API Client', () => {
  it('should construct correct URL for getMeetings', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve([]),
    });

    const { getMeetings } = await import('../api');
    await getMeetings({ status: 'completed' });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/meetings?status=completed',
      expect.objectContaining({
        headers: { 'Content-Type': 'application/json' },
      })
    );
  });

  it('should throw error on non-ok response', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: () => Promise.resolve({ detail: 'Not found' }),
    });

    const { getMeeting } = await import('../api');
    await expect(getMeeting('bad-id')).rejects.toThrow('Not found');
  });

  it('should send POST with JSON body for createMeeting', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: () => Promise.resolve({ id: '123', title: 'Test' }),
    });

    const { createMeeting } = await import('../api');
    await createMeeting({ title: 'Test Meeting' });

    expect(global.fetch).toHaveBeenCalledWith(
      '/api/meetings',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ title: 'Test Meeting' }),
      })
    );
  });

  it('should handle 204 response for deleteMeeting', async () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
    });

    const { deleteMeeting } = await import('../api');
    const result = await deleteMeeting('123');
    expect(result).toBeNull();
  });
});

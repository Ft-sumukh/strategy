/**
 * Tests for Frontend API Client and Error Envelope Handling
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApiClient } from '../lib/api/client';
import { ApiError } from '../lib/api/types';

describe('ApiClient', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient('http://localhost:8000/api/v1', 5000);
    vi.restoreAllMocks();
  });

  it('successfully parses health response and extracts data', async () => {
    const mockHealth = {
      status: 'ok',
      service: 'aegis-invest',
      version: '0.1.0',
      timestamp: '2026-09-11T14:40:00Z',
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      headers: new Headers({ 'X-Request-ID': 'mock-req-123' }),
      json: async () => mockHealth,
    });

    const result = await client.getHealth();
    expect(result.status).toBe('ok');
    expect(result.service).toBe('aegis-invest');
    expect(result.version).toBe('0.1.0');
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/health',
      expect.objectContaining({
        headers: expect.objectContaining({
          'Content-Type': 'application/json',
          Accept: 'application/json',
        }),
      })
    );
  });

  it('converts backend error envelope into strongly-typed ApiError', async () => {
    const errorEnvelope = {
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Invalid parameters provided',
        details: [{ field: 'symbol', message: 'Ticker required', type: 'value_error' }],
        request_id: 'err-req-456',
        timestamp: '2026-09-11T14:40:00Z',
      },
    };

    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 422,
      headers: new Headers({ 'X-Request-ID': 'err-req-456' }),
      json: async () => errorEnvelope,
    });

    try {
      await client.getHealth();
      expect.fail('Should have thrown ApiError');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.code).toBe('VALIDATION_ERROR');
      expect(apiErr.status).toBe(422);
      expect(apiErr.requestId).toBe('err-req-456');
      expect(apiErr.details.length).toBe(1);
      expect(apiErr.details[0].field).toBe('symbol');
    }
  });

  it('handles network failure gracefully', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Failed to fetch'));

    try {
      await client.getHealth();
      expect.fail('Should have thrown ApiError');
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.code).toBe('NETWORK_ERROR');
      expect(apiErr.status).toBe(0);
    }
  });
});

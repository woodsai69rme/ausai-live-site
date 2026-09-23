import { describe, test, expect, vi, beforeEach } from 'vitest';
import { sendJarvisCommand } from '../../src/services/jarvisService';

// Matches the response envelope produced by python/src/server/api_routes/system_api.py::_jarvis_response.
const sampleReply = {
  success: true,
  response: 'All Archon services are reporting healthy.',
  response_html: 'All Archon services are reporting healthy.',
  response_safe_html: true,
  synthetic: true,
  reason: 'local_intent',
};

const makeJsonResponse = (payload: unknown) =>
  ({
    ok: true,
    status: 200,
    json: () => Promise.resolve(payload),
    text: () => Promise.resolve(JSON.stringify(payload)),
  }) as unknown as Response;

describe('jarvisService.sendJarvisCommand', () => {
  beforeEach(() => {
    // test/setup.ts installs a default fetch mock; reset per test so
    // mockResolvedValueOnce / mockRejectedValue don't leak across tests.
    vi.mocked(global.fetch).mockReset();
  });

  test('POSTs to /api/jarvis/command with the command as JSON body', async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      // The `as unknown as Response` cast is unavoidable: jsdom's Response
      // type is stricter than BodyInit, and the project-wide mock in
      // test/setup.ts uses the same shape.
      makeJsonResponse(sampleReply)
    );

    const reply = await sendJarvisCommand('open foo bar baz');

    // retry() returns on the first successful response; no extra attempts.
    expect(global.fetch).toHaveBeenCalledTimes(1);

    const [url, init] = vi.mocked(global.fetch).mock.calls[0];
    expect(url).toBe('/api/jarvis/command');
    expect(init?.method).toBe('POST');
    expect(init?.headers).toMatchObject({ 'Content-Type': 'application/json' });
    // Body passes the input verbatim -- newlines and all -- so the
    // backend sees exactly what the user typed.
    expect(JSON.parse(String(init?.body))).toEqual({
      command: 'open foo bar baz',
    });

    // Response payload is returned verbatim so callers can branch on
    // reason / synthetic without re-parsing.
    expect(reply).toEqual(sampleReply);
  });

  test('retries up to 3 times on persistent network failure then throws', async () => {
    // Persistent rejection so every retry attempt fails. retry() back-off
    // is 500ms, 1000ms -- well under the 10s test timeout.
    vi.mocked(global.fetch).mockRejectedValue(new Error('network down'));

    await expect(sendJarvisCommand('boom')).rejects.toThrow('network down');
    // retry() default is 3 attempts; api.ts surfaces the last error.
    expect(global.fetch).toHaveBeenCalledTimes(3);
  });
});

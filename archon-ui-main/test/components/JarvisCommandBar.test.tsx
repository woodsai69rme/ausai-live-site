import React from 'react';
import { describe, test, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { JarvisCommandBar } from '../../src/components/jarvis/JarvisCommandBar';
import { ToastProvider } from '../../src/contexts/ToastContext';

// Default contract reply envelope -- tests override per-test.
const sampleReply = {
  success: true,
  response: 'Local intent hit',
  response_html: 'Local intent hit',
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

// Renders the bar under the real ToastProvider so useToast() resolves
// without resorting to a stub. Mirrors what App.tsx does in production.
const renderBar = (props: React.ComponentProps<typeof JarvisCommandBar> = {}) =>
  render(
    <ToastProvider>
      <JarvisCommandBar {...props} />
    </ToastProvider>
  );

describe('JarvisCommandBar', () => {
  beforeEach(() => {
    // Per-test fetch reset; test/setup.ts installs the default mock.
    vi.mocked(global.fetch).mockReset();
  });

  test('renders input + send button without a reply chip on first paint', () => {
    renderBar();
    expect(screen.getByLabelText('Jarvis command input')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Send/i })).toBeInTheDocument();
    expect(screen.queryByTestId('jarvis-reply')).not.toBeInTheDocument();
  });

  test('clicking Send posts the command and renders the chip with the reason label', async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      makeJsonResponse(sampleReply)
    );

    renderBar();
    fireEvent.change(screen.getByLabelText('Jarvis command input'), {
      target: { value: 'status' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    const chip = await screen.findByTestId('jarvis-reply');
    expect(chip).toHaveTextContent('Local intent');
    expect(chip).toHaveTextContent('Local intent hit');
  });

  test('pressing Enter (without Shift) submits the command', async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      makeJsonResponse({ ...sampleReply, reason: 'openrouter' })
    );

    renderBar();
    const input = screen.getByLabelText('Jarvis command input');
    fireEvent.change(input, { target: { value: 'time' } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });

    await screen.findByTestId('jarvis-reply');
    expect(global.fetch).toHaveBeenCalledTimes(1);
    expect(screen.getByTestId('jarvis-reply')).toHaveTextContent('Real NLU');
  });

  test('pressing Shift+Enter should NOT submit (newline intent)', () => {
    renderBar();
    const input = screen.getByLabelText('Jarvis command input');
    fireEvent.change(input, { target: { value: 'partial line' } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true });

    // Shift+Enter is intentionally a no-op so users can compose multi-line
    // inputs if we ever switch the input field from <input> to <textarea>.
    expect(global.fetch).not.toHaveBeenCalled();
  });

  test('onReply prop fires with the parsed envelope', async () => {
    vi.mocked(global.fetch).mockResolvedValueOnce(
      makeJsonResponse({ ...sampleReply, reason: 'no_api_key' })
    );

    const onReply = vi.fn();
    renderBar({ onReply });

    fireEvent.change(screen.getByLabelText('Jarvis command input'), {
      target: { value: 'explain kubernetes' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await waitFor(() => expect(onReply).toHaveBeenCalledTimes(1));
    expect(onReply.mock.calls[0][0].reason).toBe('no_api_key');
  });

  test('fetch rejection surfaces an error toast via the wrapped ToastProvider', async () => {
    // Persistent rejection means every retry attempt fails -- the catch
    // branch in handleSend finally fires showToast(..., 'error'). Note:
    // retry() back-off is 500ms then 1000ms before the final throw,
    // so this test consumes ~1.5s; well under the 10s vitest default.
    vi.mocked(global.fetch).mockRejectedValue(new Error('kaboom'));

    renderBar();
    fireEvent.change(screen.getByLabelText('Jarvis command input'), {
      target: { value: 'explode' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    const toast = await screen.findByText(/kaboom/i);
    expect(toast).toBeInTheDocument();
    // And the success-side reply chip must NOT render on the error path.
    expect(screen.queryByTestId('jarvis-reply')).not.toBeInTheDocument();
  });

  test('DOMPurify strips <script> from response_html before rendering (defense-in-depth)', async () => {
    // The backend already html.escape()s the body, but the bar also
    // runs the result through DOMPurify.sanitize(). This test ensures
    // that second defense stays alive even if the backend ever regresses
    // on html.escape. Assert against the LIVE DOM -- substring-only
    // checks can be fooled if DOMPurify leaves an escaped tag in place.
    const hostile = 'before <script>window.pwned=true</script> after';
    vi.mocked(global.fetch).mockResolvedValueOnce(
      makeJsonResponse({
        ...sampleReply,
        response: hostile,
        response_html: hostile,
        reason: 'local_intent',
      })
    );

    const { container } = renderBar();
    fireEvent.change(screen.getByLabelText('Jarvis command input'), {
      target: { value: 'try to inject' },
    });
    fireEvent.click(screen.getByRole('button', { name: /Send/i }));

    await screen.findByTestId('jarvis-reply');
    // No live <script> tag in the rendered subtree.
    expect(container.querySelector('script')).toBeNull();
    // Surrounding text survives the sanitize pass.
    expect(container.textContent).toContain('before');
    expect(container.textContent).toContain('after');
    // Script body must not appear in the rendered text either.
    expect(container.textContent).not.toContain('window.pwned');
  });
});

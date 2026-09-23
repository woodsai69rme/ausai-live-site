/**
 * Jarvis command service -- thin client for /api/jarvis/command.
 *
 * Mirrors the conventions in ./api.ts: re-uses the shared `apiRequest` +
 * `retry` helpers and the `/api` base path so the Vite dev proxy and the
 * production Docker routing apply uniformly.
 *
 * The endpoint contract lives in python/src/server/api_routes/system_api.py
 * (see _jarvis_response and _jarvis_call_openrouter). Every reply includes
 * the `reason` field which tells callers which arm produced the answer --
 * the React component uses this to render a friendly tone chip.
 */

import { apiRequest, retry } from "./api";

// Reason codes returned by the endpoint. Mirrors the JARVIS_REASON_*
// constants on the backend. Kept as a string union (not enum) so the
// TypeScript payload stays JSON-friendly when crossing the network.
export type JarvisReason =
  | "empty_input"
  | "local_intent"
  | "open_shape"
  | "openrouter"
  | "no_api_key"
  | "openrouter_timeout"
  | "openrouter_call_failed"
  | "empty_choices"
  | "empty_content";

export interface JarvisCommandResponse {
  success: boolean;
  response: string;
  response_html: string;
  // Backend always sets this to true once the helper runs through
  // html.escape, but keep in the type so client code can branch on it.
  response_safe_html: boolean;
  // `synthetic: true` means the reply came from the deterministic stub
  // (no_api_key echo, empty_choices echo, etc.) and not a real model.
  synthetic: boolean;
  reason: JarvisReason | string;
  error?: string;
}

export interface JarvisCommandRequest {
  command: string;
}

/**
 * Send a free-form command to Jarvis and await the response envelope.
 *
 * Retries up to 3 times with exponential backoff for transient network
 * failures (handled by `retry` from ./api.ts). Logs and rethrows
 * non-transient HTTP errors so the caller can show a toast.
 */
export async function sendJarvisCommand(
  command: string
): Promise<JarvisCommandResponse> {
  const body: JarvisCommandRequest = { command };
  return retry(() =>
    apiRequest<JarvisCommandResponse>("/jarvis/command", {
      method: "POST",
      body: JSON.stringify(body),
    })
  );
}

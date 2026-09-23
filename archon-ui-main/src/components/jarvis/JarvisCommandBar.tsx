import React, { useState } from "react";
import { Send, Sparkles, Loader2 } from "lucide-react";
import DOMPurify from "dompurify";
import {
  sendJarvisCommand,
  JarvisCommandResponse,
  JarvisReason,
} from "../../services/jarvisService";
import { useToast } from "../../contexts/ToastContext";

/**
 * JarvisCommandBar -- compact input + send button + last-reply chip.
 *
 * Lives near the top of the MainLayout content area so users can fire
 * a free-form prompt without leaving the current page. The reply lives
 * inline below the bar (modal-style overlays felt heavy for a dev
 * utility) and uses the backend's pre-escaped `response_html` so we
 * never re-concatenate user input into the DOM.
 *
 * Defense-in-depth: even though the backend runs `html.escape(...)` on
 * the response body, this component additionally runs the result
 * through DOMPurify before injecting into innerHTML. cheap and survives
 * the day someone refactors the backend escaping path.
 *
 * Reason -> tone map mirrors the one in the standalone dashboard
 * (ULTIMATE_AI_EMPIRE_ENHANCED_DASHBOARD_V2.html::renderReasonChip)
 * so the two surfaces stay visually consistent.
 *
 * Mount under a `<ToastProvider>` -- App.tsx already provides one.
 */
interface JarvisCommandBarProps {
  // Optional overridable hook so dev-mode wrappers can intercept.
  onReply?: (reply: JarvisCommandResponse) => void;
}

const REASON_TONES: Record<string, "success" | "neutral" | "warning" | "danger" | "muted"> = {
  openrouter: "success",
  local_intent: "neutral",
  open_shape: "neutral",
  no_api_key: "warning",
  openrouter_timeout: "danger",
  openrouter_call_failed: "danger",
  empty_choices: "muted",
  empty_content: "muted",
  empty_input: "muted",
};

const REASON_LABELS: Record<string, string> = {
  openrouter: "Real NLU",
  local_intent: "Local intent",
  open_shape: "Open shape",
  no_api_key: "No API key",
  openrouter_timeout: "API timeout",
  openrouter_call_failed: "API call failed",
  empty_choices: "Empty choices",
  empty_content: "Empty reply",
  empty_input: "Empty input",
};

const toneClasses: Record<string, string> = {
  success:
    "bg-emerald-500/15 text-emerald-300 border-emerald-500/40",
  neutral:
    "bg-indigo-500/15 text-indigo-300 border-indigo-500/40",
  warning:
    "bg-amber-500/15 text-amber-300 border-amber-500/40",
  danger:
    "bg-rose-500/15 text-rose-300 border-rose-500/40",
  muted:
    "bg-gray-500/15 text-gray-300 border-gray-500/40",
};

/**
 * Slim input row -- extracted so the parent component doesn't have to
 * duplicate the <input>+<button> markup across the no-reply and
 * had-reply branches.
 */
interface JarvisInputRowProps {
  value: string;
  onChange: (next: string) => void;
  onSend: () => void;
  isPending: boolean;
}

const JarvisInputRow: React.FC<JarvisInputRowProps> = ({
  value,
  onChange,
  onSend,
  isPending,
}) => {
  const disabled = isPending || value.trim().length === 0;
  return (
    <div className="flex items-center gap-2">
      <Sparkles className="w-4 h-4 text-indigo-400 shrink-0" />
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => {
          // Enter sends (without Shift) -- matches dashboard UX.
          if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            onSend();
          }
        }}
        placeholder="Ask Jarvis (status, time, hello, or any prompt)"
        className="flex-1 bg-transparent border border-gray-300/60 dark:border-gray-700/60 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/40 placeholder:text-gray-400"
        disabled={isPending}
        aria-label="Jarvis command input"
      />
      <button
        type="button"
        onClick={onSend}
        disabled={disabled}
        className="inline-flex items-center gap-1.5 rounded-md bg-gradient-to-b from-indigo-500 to-purple-600 px-3 py-2 text-sm font-medium text-white shadow-sm hover:from-indigo-400 hover:to-purple-500 disabled:opacity-50 disabled:cursor-not-allowed"
        aria-label="Send Jarvis command"
      >
        {isPending ? (
          <Loader2 className="w-4 h-4 animate-spin" />
        ) : (
          <Send className="w-4 h-4" />
        )}
        <span className="hidden sm:inline">Send</span>
      </button>
    </div>
  );
};

export const JarvisCommandBar: React.FC<JarvisCommandBarProps> = ({ onReply }) => {
  const [input, setInput] = useState("");
  const [isPending, setIsPending] = useState(false);
  const [lastReply, setLastReply] = useState<JarvisCommandResponse | null>(null);
  const { showToast } = useToast();

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isPending) return;

    setIsPending(true);
    try {
      const reply = await sendJarvisCommand(trimmed);
      setLastReply(reply);
      onReply?.(reply);

      if (!reply.success) {
        showToast(`Jarvis: ${reply.error ?? "command rejected"}`, "warning");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "unknown failure";
      showToast(`Jarvis request failed: ${message}`, "error");
    } finally {
      setInput("");
      setIsPending(false);
    }
  };

  return (
    <div
      className="rounded-xl border border-gray-200/60 bg-white/80 backdrop-blur-md p-4 shadow-sm dark:border-gray-700/60 dark:bg-gray-900/60"
      data-testid="jarvis-command-bar"
    >
      <JarvisInputRow
        value={input}
        onChange={setInput}
        onSend={handleSend}
        isPending={isPending}
      />
      {lastReply && (
        // The standalone dashboard gates `empty_input` out of its chip
        // (success=false short-circuits the modal open). The SPA renders
        // it deliberately -- on empty submit the toast alone isn't
        // enough visual feedback, so we surface the reason chip too.
        // Success vs failure both flow through this same branch; the
        // chip tone stays consistent with the dashboard contract.
        <div className="mt-3 flex items-start gap-3" data-testid="jarvis-reply">
          <span
            className={`shrink-0 inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${
              toneClasses[REASON_TONES[lastReply.reason] ?? "muted"]
            }`}
            title={`reason=${lastReply.reason} synthetic=${String(lastReply.synthetic)}`}
          >
            {REASON_LABELS[lastReply.reason] ?? lastReply.reason}
          </span>
          <div
            className="text-sm leading-relaxed text-gray-800 dark:text-gray-100 whitespace-pre-wrap break-words flex-1"
            // Backend already html.escape()s the body, but we run it
            // through DOMPurify as defense-in-depth so a future backend
            // change can't regress to XSS.
            dangerouslySetInnerHTML={{
              __html: DOMPurify.sanitize(lastReply.response_html, {
                USE_PROFILES: { html: true },
              }),
            }}
          />
        </div>
      )}
    </div>
  );
};

// Re-export the reason type so screen/page code can constrain props on
// components that wrap the bar without re-declaring the union.
export type { JarvisReason };

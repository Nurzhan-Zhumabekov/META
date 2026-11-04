import { useState } from "react";
import { ApiError, request, readableError } from "../lib/api";
import type { AppealRecord, ModerationEvent } from "../lib/types";

type Detail = {
  claim: { id: string; suspect_handle: string; status: string };
  decisions: ModerationEvent[];
  appeals: AppealRecord[];
};

function appealError(problem: unknown) {
  return problem instanceof ApiError && problem.status === 401
    ? "This private appeal link is invalid or expired. Request a new link from the moderator."
    : readableError(problem);
}

export function Appeal() {
  const [token, setToken] = useState(() => window.location.hash.slice(1));
  const [detail, setDetail] = useState<Detail | null>(null);
  const [reason, setReason] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  async function open(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setDetail(
        await request<Detail>("/appeals/access", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        }),
      );
    } catch (problem) {
      setError(appealError(problem));
    } finally {
      setBusy(false);
    }
  }
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      await request("/appeals", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token, reason: reason.trim() }),
      });
      setSent(true);
    } catch (problem) {
      setError(appealError(problem));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="review-page appeal-page">
      <span className="eyebrow">MIRRORCHECK · ACCOUNT REVIEW</span>
      <h1>Appeal a profile warning</h1>
      <p>
        A moderator reviews the explanation and the existing evidence.
        Submitting an appeal keeps the current warning in place until a decision
        is saved.
      </p>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      {!detail ? (
        <form className="reviewer-login" onSubmit={(e) => void open(e)}>
          <label>
            Private appeal access
            <input
              aria-label="Private appeal access"
              type="password"
              autoComplete="off"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              maxLength={128}
              required
            />
          </label>
          <button className="button primary" disabled={busy}>
            {busy ? "Checking access…" : "Open my report"}
          </button>
          <p>
            Use the private link issued for your report. Access expires after
            seven days.
          </p>
        </form>
      ) : (
        <article className="review-card">
          <header>
            <div>
              <h2>@{detail.claim.suspect_handle}</h2>
              <p>
                Report {detail.claim.id} · {detail.claim.status}
              </p>
            </div>
          </header>
          <div className="appeal-explanation">
            {detail.decisions.map((e) => (
              <div key={e.version}>
                <strong>Recorded decision</strong>
                <p>{e.reason}</p>
                <small>{new Date(e.at).toLocaleString("en-US")}</small>
              </div>
            ))}
          </div>
          {!detail.decisions.length && (
            <p>No explanation was recorded for this earlier decision.</p>
          )}
          {detail.appeals.map((a) => (
            <div className="appeal-explanation" key={a.id}>
              <strong>Appeal: {a.status}</strong>
              <p>{a.reason}</p>
              {a.resolution_reason && (
                <p>Moderator response: {a.resolution_reason}</p>
              )}
            </div>
          ))}
          {sent || detail.appeals.some((a) => a.status === "pending") ? (
            <p role="status" className="decision-success">
              Your appeal is awaiting a moderator’s review. The current warning
              remains until a decision.
            </p>
          ) : detail.claim.status === "confirmed" ? (
            <form className="review-decision" onSubmit={(e) => void submit(e)}>
              <label className="decision-reason">
                Why should this warning be reconsidered?
                <textarea
                  aria-label="Appeal explanation"
                  minLength={10}
                  maxLength={2000}
                  required
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                />
              </label>
              <p>
                Describe the context or explain why the visible similarities are
                misleading. Share only what the moderator needs.
              </p>
              <button
                className="button primary"
                disabled={busy || reason.trim().length < 10}
              >
                {busy ? "Submitting…" : "Submit appeal"}
              </button>
            </form>
          ) : (
            <p role="status">This report no longer adds a confirmed warning.</p>
          )}
        </article>
      )}
    </section>
  );
}

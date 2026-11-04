import { useState } from "react";
import { request, readableError } from "../lib/api";
import { useApp } from "../lib/context";
import type { AppealRecord, Claim } from "../lib/types";
import { AnalysisView } from "./Analysis";

type AppealCase = { claim: Claim; appeal: AppealRecord };

export function ModerationCenter() {
  const { refresh } = useApp();
  const [view, setView] = useState<"closed" | "history" | "appeals">("closed");
  const [cases, setCases] = useState<Claim[]>([]);
  const [appeals, setAppeals] = useState<AppealCase[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const [access, setAccess] = useState<Record<string, string>>({});
  async function load(next: typeof view) {
    setView(next);
    setError("");
    if (next === "closed") return;
    setBusy(true);
    try {
      if (next === "history")
        setCases(await request<Claim[]>("/reviewer/cases"));
      else setAppeals(await request<AppealCase[]>("/appeals/pending"));
    } catch (problem) {
      setError(readableError(problem));
    } finally {
      setBusy(false);
    }
  }
  async function grant(claim: Claim) {
    setBusy(true);
    setError("");
    try {
      const result = await request<{ token: string }>(
        `/claims/${claim.id}/appeal-access`,
        { method: "POST" },
      );
      setAccess((old) => ({
        ...old,
        [claim.id]: `${window.location.origin}/appeal#${result.token}`,
      }));
      setCases(await request<Claim[]>("/reviewer/cases"));
    } catch (problem) {
      setError(readableError(problem));
    } finally {
      setBusy(false);
    }
  }
  async function resolve(item: AppealCase, outcome: "uphold" | "overturn") {
    setBusy(true);
    setError("");
    try {
      await request(`/appeals/${item.appeal.id}/resolve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          outcome,
          reason: reasons[item.appeal.id]?.trim(),
          expected_version: item.claim.version ?? 0,
        }),
      });
      await refresh();
      await load("appeals");
    } catch (problem) {
      setError(readableError(problem));
    } finally {
      setBusy(false);
    }
  }
  return (
    <section className="moderation-center" aria-label="Decisions and appeals">
      <div className="moderation-tabs">
        <button
          className="button secondary"
          aria-expanded={view === "history"}
          onClick={() => void load(view === "history" ? "closed" : "history")}
        >
          Decision history
        </button>
        <button
          className="button secondary"
          aria-expanded={view === "appeals"}
          onClick={() => void load(view === "appeals" ? "closed" : "appeals")}
        >
          Appeal review
        </button>
      </div>
      {error && (
        <p role="alert" className="form-error">
          {error}
        </p>
      )}
      {busy && <p role="status">Loading or saving review…</p>}
      {view === "history" &&
        cases
          .filter((c) => c.status !== "under_review")
          .map((claim) => (
            <article className="review-card" key={claim.id}>
              <header>
                <div>
                  <h2>@{claim.suspect_handle}</h2>
                  <p>
                    Report {claim.id} · {claim.status}
                  </p>
                </div>
              </header>
              <ol className="decision-timeline">
                {(claim.history ?? []).map((e) => (
                  <li key={e.version}>
                    <strong>{e.kind.replaceAll("_", " ")}</strong>
                    <p>{e.reason}</p>
                    <small>
                      {e.actor} · {new Date(e.at).toLocaleString("en-US")}
                    </small>
                    {e.to_status && <p>Saved outcome: {e.to_status}</p>}
                  </li>
                ))}
              </ol>
              {!claim.history?.length && (
                <p className="legacy-evidence">
                  Earlier decision imported. No reason was recorded in that
                  version.
                </p>
              )}
              {claim.status === "confirmed" && (
                <div className="review-decision">
                  <button
                    className="button secondary"
                    disabled={busy}
                    onClick={() => void grant(claim)}
                  >
                    Create appeal access for @{claim.suspect_handle}
                  </button>
                  <p>
                    Issue a seven-day link only after verifying the recipient’s
                    right to appeal. This prototype does not verify Instagram
                    ownership. In a public sandbox, use this link in the same
                    browser session.
                  </p>
                  {access[claim.id] && (
                    <a
                      className="button secondary"
                      href={access[claim.id]}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open private appeal for @{claim.suspect_handle}
                    </a>
                  )}
                </div>
              )}
            </article>
          ))}
      {view === "appeals" && !busy && !appeals.length && (
        <p>No pending appeals.</p>
      )}
      {view === "appeals" &&
        appeals.map((item) => (
          <article className="review-card" key={item.appeal.id}>
            <header>
              <div>
                <h2>Appeal · @{item.claim.suspect_handle}</h2>
                <p>
                  Report {item.claim.id} · The existing warning remains while
                  this appeal is pending.
                </p>
              </div>
            </header>
            <blockquote className="appeal-statement">
              {item.appeal.reason}
            </blockquote>
            <div className="review-evidence">
              {(["original", "suspect"] as const).map(
                (kind) =>
                  item.claim.evidence?.[kind] && (
                    <figure key={kind}>
                      <figcaption>
                        {kind === "original"
                          ? "Claimed original"
                          : "Reported account"}
                      </figcaption>
                      <img
                        src={`/api${item.claim.evidence[kind]}`}
                        alt={`Processed ${kind} evidence`}
                      />
                    </figure>
                  ),
              )}
            </div>
            <AnalysisView claim={item.claim} detailed />
            <div className="review-decision">
              <label className="decision-reason">
                Appeal decision reason
                <textarea
                  aria-label={`Appeal decision reason for ${item.appeal.id}`}
                  value={reasons[item.appeal.id] ?? ""}
                  minLength={10}
                  maxLength={2000}
                  onChange={(e) =>
                    setReasons((old) => ({
                      ...old,
                      [item.appeal.id]: e.target.value,
                    }))
                  }
                />
              </label>
              <div>
                <button
                  className="button secondary"
                  disabled={
                    busy || (reasons[item.appeal.id]?.trim().length ?? 0) < 10
                  }
                  onClick={() => void resolve(item, "uphold")}
                >
                  Uphold warning
                </button>
                <button
                  className="button primary"
                  disabled={
                    busy || (reasons[item.appeal.id]?.trim().length ?? 0) < 10
                  }
                  onClick={() => void resolve(item, "overturn")}
                >
                  Overturn and remove this warning
                </button>
              </div>
            </div>
          </article>
        ))}
    </section>
  );
}

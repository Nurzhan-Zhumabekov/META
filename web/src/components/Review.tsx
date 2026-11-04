import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, readableError, request } from "../lib/api";
import { accounts, accountByHandle } from "../lib/data";
import { useApp } from "../lib/context";
import type { Claim } from "../lib/types";
import { AnalysisView } from "./Analysis";
import { Avatar, EmptyState } from "./Common";
import { Icon } from "./Icon";
import { EvidenceRegions } from "./ScreenshotInspection";
import { ModerationCenter } from "./ModerationCenter";

export function Review() {
  const { refresh, notify, service } = useApp();
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [claims, setClaims] = useState<Claim[]>([]);
  const [token, setToken] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");
  const [completed, setCompleted] = useState<string | null>(null);
  const [reasons, setReasons] = useState<Record<string, string>>({});
  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      await request("/reviewer/session");
      const rows = await request<Claim[]>("/claims/pending");
      setClaims(
        rows.sort((a, b) =>
          (b.created_at ?? "").localeCompare(a.created_at ?? ""),
        ),
      );
      setAuthenticated(true);
    } catch (problem) {
      if (problem instanceof ApiError && problem.status === 401)
        setAuthenticated(false);
      else setError(readableError(problem));
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => {
    void load();
  }, [load]);
  async function login(event: React.FormEvent) {
    event.preventDefault();
    setBusy("login");
    setError("");
    try {
      if (service?.public_demo)
        await request("/demo/reviewer", { method: "POST" });
      else
        await request("/reviewer/session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });
      setToken("");
      await load();
    } catch (problem) {
      setError(readableError(problem));
    } finally {
      setBusy("");
    }
  }
  async function decide(claim: Claim, status: "confirmed" | "rejected") {
    setBusy(claim.id);
    setError("");
    try {
      await request(`/claims/${claim.id}/status`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          status,
          reason: reasons[claim.id]?.trim(),
          expected_version: claim.version ?? 0,
        }),
      });
      await refresh();
      setCompleted(claim.suspect_handle);
      setClaims((old) => old.filter((row) => row.id !== claim.id));
      notify(
        status === "confirmed"
          ? "Label added to the profile"
          : "Report dismissed",
      );
    } catch (problem) {
      setError(readableError(problem));
      if (problem instanceof ApiError && problem.status === 401)
        setAuthenticated(false);
    } finally {
      setBusy("");
    }
  }
  return (
    <section className="review-page">
      <header className="review-page-heading">
        <div>
          <span className="eyebrow">SAFETY CENTER</span>
          <h1>Report review</h1>
          <p>
            Review the evidence and decide whether to add a profile warning.
          </p>
        </div>
        {authenticated && (
          <button
            className="button secondary"
            onClick={() => {
              void request("/reviewer/session", { method: "DELETE" })
                .then(() => {
                  setAuthenticated(false);
                  setClaims([]);
                })
                .catch((problem) => setError(readableError(problem)));
            }}
          >
            <Icon name="logout" size={16} />
            Log out
          </button>
        )}
      </header>
      {error && (
        <p className="form-error" role="alert">
          {error}
        </p>
      )}
      {loading ? (
        <div className="review-skeleton" aria-label="Loading reports">
          <div />
          <div />
          <div />
        </div>
      ) : !authenticated ? (
        <form className="reviewer-login" onSubmit={login}>
          <span className="login-symbol">
            <Icon name="shield" size={34} />
          </span>
          <h2>
            {service?.public_demo ? "Moderator sandbox" : "Moderator access"}
          </h2>
          <p>
            {service?.public_demo
              ? "Try the moderator role for reports in your own demonstration session. Other visitors and the developer’s reports are inaccessible."
              : "Enter the moderator code for this app to review reports."}
          </p>
          {!service?.public_demo && (
            <label>
              Moderator code
              <input
                type="password"
                autoComplete="current-password"
                value={token}
                onChange={(e) => setToken(e.target.value)}
                required
                maxLength={512}
              />
            </label>
          )}
          <button className="button primary full" disabled={!!busy}>
            {busy
              ? "Logging in…"
              : service?.public_demo
                ? "Enter moderator sandbox"
                : "Log in"}
          </button>
          <p className="dialog-footnote">
            This code grants access to the demo app. It is not an Instagram
            password.
          </p>
        </form>
      ) : (
        <>
          <div className="review-toolbar">
            <strong>
              Awaiting a decision <span>{claims.length}</span>
            </strong>
            <button className="text-button" onClick={() => void load()}>
              Refresh
            </button>
          </div>
          <ModerationCenter />
          {completed && (
            <div className="decision-success" role="status">
              <Icon name="check" size={18} />
              <span>Decision saved.</span>
              {accountByHandle(completed) && (
                <Link to={`/profile/${completed}`}>
                  View profile
                  <Icon name="chevron" size={15} />
                </Link>
              )}
            </div>
          )}
          {!claims.length && (
            <EmptyState icon="shield" title="All reports reviewed">
              New reports will appear here once submitted.
            </EmptyState>
          )}
          {claims.map((claim) => (
            <article
              className="review-card"
              key={claim.id}
              data-testid={`review-${claim.id}`}
            >
              <header>
                <Avatar
                  account={
                    accountByHandle(claim.suspect_handle) ?? {
                      ...accounts[1],
                      handle: claim.suspect_handle,
                    }
                  }
                  size="sm"
                />
                <div>
                  <h2>@{claim.suspect_handle}</h2>
                  <p>
                    Reported by @{claim.owner_handle} · № {claim.id}
                  </p>
                </div>
                <span className="review-card-status">Under review</span>
              </header>
              {claim.evidence?.original && claim.evidence?.suspect ? (
                <div className="review-evidence">
                  {(["original", "suspect"] as const).map((kind) => (
                    <figure key={kind}>
                      <figcaption>
                        {kind === "original"
                          ? "Claimed original"
                          : "Reported account"}
                      </figcaption>
                      <a
                        href={`/api${claim.evidence![kind]}`}
                        target="_blank"
                        rel="noreferrer"
                      >
                        <EvidenceRegions
                          src={`/api${claim.evidence![kind]}`}
                          alt={
                            kind === "original"
                              ? "Evidence: original profile"
                              : "Evidence: reported profile"
                          }
                          boxes={claim.analysis.screenshot_tools?.photos.matches.map(
                            (match) =>
                              claim.analysis.screenshot_tools!.photos[
                                kind === "original"
                                  ? "original_boxes"
                                  : "suspect_boxes"
                              ][
                                match[
                                  kind === "original"
                                    ? "original_index"
                                    : "suspect_index"
                                ]
                              ],
                          )}
                        />
                      </a>
                    </figure>
                  ))}
                </div>
              ) : (
                <p className="legacy-evidence">
                  <Icon name="warning" size={17} />
                  The screenshots were not stored for this older report. A
                  complete review requires new evidence.
                </p>
              )}
              <AnalysisView claim={claim} detailed />
              <div className="review-decision">
                <p>
                  <Icon name="shield" size={17} />
                  Review the matches and the basis of the report. AI scores do
                  not replace your judgment.
                </p>
                <label className="decision-reason">
                  Decision reason
                  <textarea
                    aria-label={`Decision reason for @${claim.suspect_handle}`}
                    placeholder="Explain which evidence supports confirmation or dismissal."
                    minLength={10}
                    maxLength={2000}
                    value={reasons[claim.id] ?? ""}
                    onChange={(e) =>
                      setReasons((old) => ({
                        ...old,
                        [claim.id]: e.target.value,
                      }))
                    }
                  />
                  <small>
                    Required · at least 10 characters · saved in the private
                    decision history
                  </small>
                </label>
                <div>
                  <button
                    className="button danger-solid"
                    disabled={
                      !!busy || (reasons[claim.id]?.trim().length ?? 0) < 10
                    }
                    onClick={() => void decide(claim, "confirmed")}
                  >
                    {busy === claim.id ? "Saving…" : "Confirm impersonation"}
                  </button>
                  <button
                    className="button secondary"
                    disabled={
                      !!busy || (reasons[claim.id]?.trim().length ?? 0) < 10
                    }
                    onClick={() => void decide(claim, "rejected")}
                  >
                    Dismiss report
                  </button>
                </div>
              </div>
            </article>
          ))}
        </>
      )}
    </section>
  );
}

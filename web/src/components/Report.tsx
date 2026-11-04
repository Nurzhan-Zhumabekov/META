import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fileError, profileFacts, readableError, request } from "../lib/api";
import type { FactValues } from "../lib/api";
import { useApp } from "../lib/context";
import type { Account, Claim, ScreenshotInspection } from "../lib/types";
import { InspectionPreview } from "./ScreenshotInspection";
import { Avatar } from "./Common";
import { AnalysisView } from "./Analysis";
import { Dialog } from "./Dialog";
import { Icon } from "./Icon";

export function ReportDialog({
  account,
  onClose,
}: {
  account: Account;
  onClose: () => void;
}) {
  const { user, service, connectionError, refresh, notify } = useApp();
  const navigate = useNavigate();
  const [step, setStep] = useState<
    "reason" | "evidence" | "working" | "result"
  >("reason");
  const [original, setOriginal] = useState<File | null>(null);
  const [suspect, setSuspect] = useState<File | null>(null);
  const [owner, setOwner] = useState(user.handle);
  const [error, setError] = useState("");
  const [claim, setClaim] = useState<Claim>();
  const [includeML, setIncludeML] = useState(false);
  const [includePair, setIncludePair] = useState(false);
  const [originalText, setOriginalText] = useState({
    display_name: user.name,
    bio: user.bio,
  });
  const [facts, setFacts] = useState<FactValues>({
    handle: account.handle,
    display_name: account.name,
    bio: account.bio,
    num_posts: String(account.posts),
    num_followers: String(account.followers),
    num_following: String(account.following),
    has_profile_picture: true,
    has_external_url: false,
    is_private: false,
  });
  const controller = useRef<AbortController | null>(null);
  const [inspection, setInspection] = useState<ScreenshotInspection | null>(
    null,
  );
  const [inspecting, setInspecting] = useState(false);
  const [inspectionError, setInspectionError] = useState("");
  const [ocrReviewed, setOcrReviewed] = useState(false);
  const [inspectionAttempt, setInspectionAttempt] = useState(0);
  useEffect(() => {
    setInspection(null);
    setOcrReviewed(false);
    setInspectionError("");
    if (!original || !suspect || !service?.evidence_tools?.ready) {
      setInspecting(false);
      return;
    }
    const abort = new AbortController();
    let active = true;
    const timeout = setTimeout(() => abort.abort(), 125000);
    setInspecting(true);
    const data = new FormData();
    data.set("original", original);
    data.set("suspect_image", suspect);
    data.set("owner", owner);
    data.set("suspect", account.handle);
    void request<ScreenshotInspection>("/evidence/inspect", {
      method: "POST",
      body: data,
      signal: abort.signal,
    })
      .then((result) => {
        if (!active) return;
        if (
          !result.redaction?.applied ||
          !result.redaction.previews?.original ||
          !result.redaction.previews?.suspect
        )
          throw new Error(
            "The service could not prepare safe screenshots. Nothing was sent to Meta AI.",
          );
        setInspection(result);
        const candidate = result.suspect.fields,
          originalFields = result.original.fields;
        const text = (key: string, fields: typeof candidate) =>
          typeof fields[key]?.value === "string"
            ? String(fields[key].value)
            : "";
        setOwner(text("handle", originalFields));
        setOriginalText({
          display_name: text("display_name", originalFields),
          bio: text("bio", originalFields),
        });
        setFacts((old) => ({
          ...old,
          display_name: text("display_name", candidate),
          bio: text("bio", candidate),
          num_posts: candidate.num_posts
            ? String(candidate.num_posts.value)
            : "",
          num_followers: candidate.num_followers
            ? String(candidate.num_followers.value)
            : "",
          num_following: candidate.num_following
            ? String(candidate.num_following.value)
            : "",
        }));
      })
      .catch((problem) => {
        if (active) setInspectionError(readableError(problem));
      })
      .finally(() => {
        if (active) setInspecting(false);
        clearTimeout(timeout);
      });
    return () => {
      active = false;
      abort.abort();
      clearTimeout(timeout);
    };
    // A new file pair triggers inspection. Editing the owner afterward is manual.
  }, [original, suspect, service?.evidence_tools?.ready, inspectionAttempt]);
  useEffect(() => {
    setIncludeML(service?.profile_ml.ready ?? false);
  }, [service?.profile_ml.ready]);
  useEffect(() => {
    setIncludePair(service?.pair_ml?.ready ?? false);
  }, [service?.pair_ml?.ready]);
  useEffect(() => () => controller.current?.abort(), []);
  const choose = (
    file: File | undefined,
    setter: (value: File | null) => void,
  ) => {
    if (!file) return;
    const problem = fileError(file);
    if (problem) {
      setError(problem);
      return;
    }
    setError("");
    setter(file);
  };
  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    if (!original || !suspect) {
      setError(
        "Attach two screenshots: your profile and the reported profile.",
      );
      return;
    }
    if (!/^@?[a-zA-Z0-9_.]{1,30}$/.test(owner.trim())) {
      setError(
        "Check your username: use Latin letters, numbers, periods and underscores.",
      );
      return;
    }
    const data = new FormData();
    data.set("owner", owner.trim().replace(/^@/, ""));
    data.set("suspect", account.handle);
    data.set("original", original);
    data.set("suspect_image", suspect);
    if (inspection) {
      if (!ocrReviewed) {
        setError("Review the recognized data before submitting.");
        return;
      }
      data.set("inspection_id", inspection.inspection_id);
      data.set("ocr_reviewed", String(ocrReviewed));
    }
    try {
      if (includeML)
        data.set("profile_facts", JSON.stringify(profileFacts(facts)));
      if (includeML && includePair && service?.pair_ml?.ready) {
        if (!originalText.bio.trim())
          throw new Error(
            "Add the original profile bio or turn off the two-profile comparison.",
          );
        data.set(
          "original_profile_facts",
          JSON.stringify({
            handle: owner.trim().replace(/^@/, ""),
            ...originalText,
          }),
        );
      }
    } catch (problem) {
      setError(readableError(problem));
      return;
    }
    setStep("working");
    controller.current = new AbortController();
    const timeout = setTimeout(() => controller.current?.abort(), 90000);
    try {
      const result = await request<Claim>("/claims", {
        method: "POST",
        body: data,
        signal: controller.current.signal,
      });
      setClaim(result);
      await refresh();
      setStep("result");
      notify("Report submitted for review");
    } catch (problem) {
      setError(
        problem instanceof DOMException && problem.name === "AbortError"
          ? "The analysis timed out. Check the profile status before submitting again."
          : readableError(problem),
      );
      setStep("evidence");
    } finally {
      clearTimeout(timeout);
      controller.current = null;
    }
  }
  return (
    <Dialog
      title={step === "result" ? "Report submitted" : "Report"}
      onClose={onClose}
      className={`report-dialog report-${step}`}
      busy={step === "working"}
    >
      {step === "reason" && (
        <div className="report-reasons">
          <div className="report-account">
            <Avatar account={account} size="lg" linked={false} />
            <strong>@{account.handle}</strong>
          </div>
          <h3>Why are you reporting this account?</h3>
          <p>
            We will compare the evidence and send it to a moderator. A report
            does not automatically add a label.
          </p>
          <button className="report-reason" onClick={() => setStep("evidence")}>
            Pretending to be someone else
            <Icon name="chevron" size={18} />
          </button>
          <button className="report-cancel" onClick={onClose}>
            Cancel
          </button>
        </div>
      )}
      {step === "evidence" && (
        <form className="report-form" onSubmit={submit}>
          <div className="report-step">
            <span>1</span>
            <i />
            <span className="current">2</span>
            <i />
            <span>3</span>
            <strong>Evidence</strong>
          </div>
          <h3>Help us compare the accounts</h3>
          <p className="muted">
            Attach screenshots showing the name, bio and posts of both profiles.
          </p>
          <label className="field-label">
            Your original account
            <div className="handle-field">
              <span>@</span>
              <input
                value={owner}
                onChange={(e) => {
                  setOwner(e.target.value);
                  setOriginalText(
                    e.target.value.replace(/^@/, "").toLowerCase() ===
                      user.handle.toLowerCase()
                      ? { display_name: user.name, bio: user.bio }
                      : { display_name: "", bio: "" },
                  );
                }}
                autoComplete="off"
                maxLength={31}
                aria-label="Your original account"
                required
              />
            </div>
          </label>
          <div className="proof-pair">
            <ProofUpload
              label="Your profile screenshot"
              title="Your account"
              file={original}
              onChoose={(file) => choose(file, setOriginal)}
              onClear={() => setOriginal(null)}
            />
            <ProofUpload
              label="Reported profile screenshot"
              title={`@${account.handle}`}
              file={suspect}
              onChoose={(file) => choose(file, setSuspect)}
              onClear={() => setSuspect(null)}
            />
          </div>
          {inspecting && (
            <div className="inspection-progress" role="status">
              PaddleOCR is reading the screenshots. imagededup is comparing
              photos and Presidio is checking for personal data…
            </div>
          )}
          {inspectionError && (
            <p className="form-error" role="alert">
              {inspectionError}{" "}
              <button
                type="button"
                className="text-button"
                onClick={() => setInspectionAttempt((v) => v + 1)}
              >
                Retry analysis
              </button>
            </p>
          )}
          {service?.privacy_redaction_required &&
            !service.evidence_tools?.ready && (
              <p className="form-error" role="alert">
                Contact redaction is temporarily unavailable. Nothing was sent
                to Meta AI.
              </p>
            )}
          {inspection && original && suspect && (
            <InspectionPreview
              inspection={inspection}
              reviewed={ocrReviewed}
              onReview={setOcrReviewed}
            />
          )}
          {service?.profile_ml.ready && (
            <details
              className="profile-facts"
              open={inspection ? true : undefined}
            >
              <summary>
                <Icon name="shield" size={16} />
                Additional profile checks<span>Optional</span>
              </summary>
              <p className="muted">
                {inspection
                  ? "These fields were read from the screenshots. Review and correct them before submitting."
                  : "These are demo profile details. Review them before submitting; they were not imported from Instagram."}
              </p>
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={includeML}
                  onChange={(e) => setIncludeML(e.target.checked)}
                />
                Include profile details in the analysis
              </label>
              {includeML && (
                <div className="facts-fields">
                  <label>
                    Name
                    <input
                      value={facts.display_name}
                      maxLength={100}
                      onChange={(e) =>
                        setFacts({ ...facts, display_name: e.target.value })
                      }
                    />
                  </label>
                  <label>
                    Bio
                    <textarea
                      value={facts.bio}
                      maxLength={500}
                      rows={2}
                      onChange={(e) =>
                        setFacts({ ...facts, bio: e.target.value })
                      }
                    />
                  </label>
                  <div className="fact-counts">
                    {(
                      [
                        ["num_posts", "Posts"],
                        ["num_followers", "Followers"],
                        ["num_following", "Following"],
                      ] as const
                    ).map(([key, label]) => (
                      <label key={key}>
                        {label}
                        <input
                          type="number"
                          inputMode="numeric"
                          min="0"
                          max="2147483647"
                          step="1"
                          value={facts[key]}
                          onChange={(e) =>
                            setFacts({ ...facts, [key]: e.target.value })
                          }
                          required
                        />
                      </label>
                    ))}
                  </div>
                  {(
                    [
                      ["has_profile_picture", "Has a profile photo"],
                      ["is_private", "Private account"],
                      ["has_external_url", "Has an external link"],
                    ] as const
                  ).map(([key, label]) => (
                    <label className="checkbox-row" key={key}>
                      <input
                        type="checkbox"
                        checked={facts[key]}
                        onChange={(e) =>
                          setFacts({ ...facts, [key]: e.target.checked })
                        }
                      />
                      {label}
                    </label>
                  ))}
                  {service?.pair_ml?.ready && (
                    <>
                      <label className="checkbox-row">
                        <input
                          type="checkbox"
                          checked={includePair}
                          onChange={(e) => setIncludePair(e.target.checked)}
                        />
                        Compare with the original profile
                      </label>
                      {includePair && (
                        <div className="facts-fields original-facts">
                          <strong>
                            Original profile · @{owner.replace(/^@/, "")}
                          </strong>
                          <p className="muted">
                            Review the original name and bio. The model compares
                            the text of both accounts; the avatar and follower
                            count do not affect this score.
                          </p>
                          <label>
                            Original profile name
                            <input
                              aria-label="Original profile name"
                              maxLength={100}
                              value={originalText.display_name}
                              onChange={(e) =>
                                setOriginalText({
                                  ...originalText,
                                  display_name: e.target.value,
                                })
                              }
                            />
                          </label>
                          <label>
                            Original profile bio
                            <textarea
                              aria-label="Original profile bio"
                              maxLength={500}
                              rows={3}
                              value={originalText.bio}
                              onChange={(e) =>
                                setOriginalText({
                                  ...originalText,
                                  bio: e.target.value,
                                })
                              }
                            />
                          </label>
                        </div>
                      )}
                    </>
                  )}
                </div>
              )}
            </details>
          )}
          {error && (
            <p className="form-error" role="alert">
              <Icon name="warning" size={17} />
              {error}
            </p>
          )}
          {connectionError && (
            <p className="form-error">
              Cannot connect to the service.{" "}
              <button
                type="button"
                className="text-button"
                onClick={() => void refresh()}
              >
                Reconnect
              </button>
            </p>
          )}
          <p className="privacy-note">
            <Icon name="shield" size={16} />
            {service?.provider === "meta"
              ? "Contact details are automatically redacted locally before sending to Meta AI. Review the prepared images. A moderator decides whether to add a label."
              : "The screenshots will be compared and sent to a moderator for review."}
          </p>
          <button
            className="button primary full"
            type="submit"
            disabled={
              (!!service && !service.ready) ||
              inspecting ||
              (service?.privacy_redaction_required &&
                (!service.evidence_tools?.ready || !inspection)) ||
              (service?.provider === "meta" &&
                service?.evidence_tools?.ready &&
                !inspection) ||
              !!(inspection && !ocrReviewed)
            }
          >
            Submit report
          </button>
          <p className="dialog-footnote">
            Account similarity alone does not prove impersonation.
          </p>
        </form>
      )}
      {step === "working" && (
        <div className="report-working" role="status" aria-live="polite">
          <div className="analysis-spinner">
            <Icon name="shield" size={35} />
          </div>
          <h3>Comparing the evidence</h3>
          <p>
            Checking screenshot matches and profile details. This may take a
            little time.
          </p>
          <div className="working-source">
            <span className="pulse-dot" />
            {service?.provider === "meta"
              ? "Analysis with Meta AI"
              : "Image analysis"}
          </div>
          <p className="muted">
            Keep this window open until the analysis is complete.
          </p>
        </div>
      )}
      {step === "result" && claim && (
        <div className="report-success">
          <div className="success-symbol">
            <Icon name="check" size={34} />
          </div>
          <h3>Thank you. We received your report.</h3>
          <p>
            The account has been sent for review. A moderator will decide after
            examining the evidence.
          </p>
          <div className="report-receipt">
            <span>
              <Icon name="clock" size={17} />
              Under review
            </span>
            <small>№ {claim.id}</small>
          </div>
          <details className="result-details">
            <summary>What we found</summary>
            <AnalysisView claim={claim} />
          </details>
          <button
            className="button primary full"
            onClick={() => {
              navigate(`/profile/${account.handle}`);
              onClose();
            }}
          >
            Go to profile
          </button>
          <button className="button quiet full" onClick={onClose}>
            Done
          </button>
        </div>
      )}
    </Dialog>
  );
}
function ProofUpload({
  label,
  title,
  file,
  onChoose,
  onClear,
}: {
  label: string;
  title: string;
  file: File | null;
  onChoose: (file: File | undefined) => void;
  onClear: () => void;
}) {
  const [preview, setPreview] = useState("");
  useEffect(() => {
    if (!file) {
      setPreview("");
      return;
    }
    const url = URL.createObjectURL(file);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [file]);
  return (
    <div className="proof-item">
      <strong>{title}</strong>
      <label
        className={`proof-upload ${file ? "has-file" : ""}`}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          onChoose(e.dataTransfer.files[0]);
        }}
      >
        {preview ? (
          <img src={preview} alt={label} />
        ) : (
          <>
            <Icon name="upload" size={26} />
            <span>Choose screenshot</span>
            <small>JPG, PNG, WebP · up to 5 MB</small>
          </>
        )}
        <input
          type="file"
          accept="image/jpeg,image/png,image/webp"
          aria-label={label}
          onChange={(e) => onChoose(e.target.files?.[0])}
        />
      </label>
      {file && (
        <div className="file-caption">
          <span>{file.name}</span>
          <button
            type="button"
            aria-label={`Remove ${label.toLowerCase()}`}
            onClick={onClear}
          >
            <Icon name="close" size={14} />
          </button>
        </div>
      )}
    </div>
  );
}

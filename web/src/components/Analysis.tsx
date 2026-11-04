import type { Claim } from "../lib/types";
import { Icon } from "./Icon";
import { englishText, hasEnglishTranslation } from "../lib/english";

export function AnalysisView({
  claim,
  detailed = false,
}: {
  claim: Claim;
  detailed?: boolean;
}) {
  const analysis = claim.analysis;
  const risk = analysis.profile_ml;
  const pair = analysis.pair_ml;
  const tools = analysis.screenshot_tools;
  return (
    <div className="analysis-view">
      <div className="analysis-source">
        <Icon name="shield" size={18} />
        <strong>
          {analysis.provider === "meta"
            ? "Meta AI"
            : analysis.provider === "mock"
              ? "Demo analysis"
              : "Image comparison"}
        </strong>
        {detailed && analysis.model && <span>{analysis.model}</span>}
      </div>
      {analysis.summary && (
        <p className="analysis-summary">{englishText(analysis.summary)}</p>
      )}
      {analysis.summary && hasEnglishTranslation(analysis.summary) && (
        <p className="muted">
          Translated to English from the original analysis.
        </p>
      )}
      <div className="analysis-metrics">
        {pair && (
          <div>
            <span>Content reuse signals · ML</span>
            <strong>
              {pair.risk_score === null
                ? "—"
                : Math.round(pair.risk_score * 100)}
              {pair.risk_score !== null && <small>%</small>}
            </strong>
            <p>
              {pair.risk_score === null
                ? "Not enough data from both profiles"
                : "Comparing names, bios and usernames"}
            </p>
          </div>
        )}
        <div>
          <span>Image and name similarity</span>
          <strong>
            {Math.round(claim.score * 100)}
            <small>%</small>
          </strong>
          <p>Content reuse score</p>
        </div>
        {risk && (
          <div>
            <span>Spam patterns · ML</span>
            <strong>
              {Math.round(risk.risk_score * 100)}
              <small>%</small>
            </strong>
            <p>An independent signal, not a content reuse score</p>
          </div>
        )}
      </div>
      {pair && (
        <p className="muted">
          The content reuse model was trained on synthetic pairs. This score is
          not an impersonation probability; performance on real accounts has not
          yet been established.
        </p>
      )}
      {tools && (
        <div className="inspection-result">
          <strong>Screenshot inspection</strong>
          <p>
            PaddleOCR extracted the fields • imagededup: matched photos —{" "}
            {tools.photos.count} • Presidio: personal data regions flagged —{" "}
            {tools.original.privacy.count + tools.suspect.privacy.count}
          </p>
          <small>
            Matched photos and extracted fields were reviewed before submission.
            Scores do not establish account ownership.
          </small>
        </div>
      )}
      {analysis.privacy_redaction?.applied && (
        <div className="inspection-result">
          <strong>Presidio: redacted before Meta AI</strong>
          <p>
            Regions masked: {analysis.privacy_redaction.regions_masked}. The
            moderator sees the same processed images that were sent to the
            model.
          </p>
        </div>
      )}
      {detailed && (
        <div className="evidence-analysis">
          {[
            ["Matches", analysis.evidence],
            ["Differences", analysis.differences],
          ].map(([title, items]) =>
            Array.isArray(items) && items.length > 0 ? (
              <section key={String(title)}>
                <h4>{String(title)}</h4>
                <ul>
                  {items.map((item, i) => (
                    <li key={i}>{englishText(String(item))}</li>
                  ))}
                </ul>
              </section>
            ) : null,
          )}
          {risk && risk.factors.length > 0 && (
            <details>
              <summary>ML factors</summary>
              <ul>
                {risk.factors.map((factor, i) => (
                  <li key={i}>
                    {englishText(factor.label)}: {factor.value} —{" "}
                    {factor.direction === "raises" ? "increases" : "decreases"}{" "}
                    the model score
                  </li>
                ))}
              </ul>
              {risk.out_of_range_features.length > 0 && (
                <p>Some values are outside the training data range.</p>
              )}
            </details>
          )}
          {pair && pair.factors.length > 0 && (
            <details>
              <summary>Why ML detects content reuse</summary>
              <ul>
                {pair.factors.map((factor, i) => (
                  <li key={i}>
                    {englishText(factor.label)}: {factor.value.toFixed(2)} —{" "}
                    {factor.direction === "raises"
                      ? "increases"
                      : factor.direction === "lowers"
                        ? "decreases"
                        : "does not change"}{" "}
                    the score
                  </li>
                ))}
              </ul>
              <ul>
                {pair.limitations.map((text, i) => (
                  <li key={i}>{englishText(text)}</li>
                ))}
              </ul>
            </details>
          )}
        </div>
      )}
      <p className="analysis-disclaimer">
        <Icon name="clock" size={15} />
        Similarity and ML scores do not prove impersonation. The final decision
        is made by a person.
      </p>
      {detailed && analysis.limitations?.length ? (
        <details className="limitations">
          <summary>Analysis limitations</summary>
          <ul>
            {analysis.limitations.map((text, i) => (
              <li key={i}>{englishText(text)}</li>
            ))}
          </ul>
          <p>
            The ML model was trained on a small historical fake/spam dataset.
            Its score is not an impersonation probability.
          </p>
        </details>
      ) : null}
    </div>
  );
}

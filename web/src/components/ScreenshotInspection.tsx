import type { ScreenshotInspection } from "../lib/types";
import { englishText } from "../lib/english";

export function EvidenceRegions({
  src,
  alt,
  boxes = [],
}: {
  src: string;
  alt: string;
  boxes?: number[][];
}) {
  return (
    <div className="evidence-regions">
      <img src={src} alt={alt} />
      {boxes.map((box, i) => (
        <span
          key={i}
          className="photo-region"
          aria-label={`Matched photo ${i + 1}`}
          style={{
            left: `${box[0] * 100}%`,
            top: `${box[1] * 100}%`,
            width: `${(box[2] - box[0]) * 100}%`,
            height: `${(box[3] - box[1]) * 100}%`,
          }}
        >
          <b>{i + 1}</b>
        </span>
      ))}
    </div>
  );
}

export function InspectionPreview({
  inspection,
  reviewed,
  onReview,
}: {
  inspection: ScreenshotInspection;
  reviewed: boolean;
  onReview: (v: boolean) => void;
}) {
  const pii =
    inspection.original.privacy.count + inspection.suspect.privacy.count;
  const warnings = [
    ...inspection.original.warnings,
    ...inspection.suspect.warnings,
  ];
  return (
    <section className="inspection-preview" aria-label="Screenshot preview">
      <strong>Fields extracted by PaddleOCR</strong>
      <p>
        The name, bio and available counts have been filled in below. Correct
        any misread letters and check the numbers. Unreadable fields are left
        blank.
      </p>
      <div className="inspection-copies">
        <b>imagededup: matched photos — {inspection.photos.count}</b>
        <span>Comparing individual photo regions, excluding avatars</span>
        {inspection.photos.matches.some(
          (m) =>
            m.verification === "orb_geometry" ||
            m.verification === "sift_geometry",
        ) && (
          <span>
            Some matches use local feature geometry to handle crops or
            rotations. Shared visual detail does not establish ownership.
          </span>
        )}
      </div>
      <div className="inspection-redaction">
        <strong>
          Redacted before sending to Meta AI:{" "}
          {inspection.redaction.regions_masked}
        </strong>
        <p>
          Contact details are masked on the server. The previews show the exact
          JPEG images that Meta AI will receive. Unredacted originals are not
          sent to Meta.
        </p>
        <div className="inspection-image-pair">
          {(["original", "suspect"] as const).map((side) => (
            <figure key={side}>
              <EvidenceRegions
                src={inspection.redaction.previews[side]}
                alt={
                  side === "original"
                    ? "For Meta AI: original profile"
                    : "For Meta AI: reported profile"
                }
                boxes={inspection.photos.matches.map(
                  (match) =>
                    inspection.photos[
                      side === "original" ? "original_boxes" : "suspect_boxes"
                    ][
                      match[
                        side === "original" ? "original_index" : "suspect_index"
                      ]
                    ],
                )}
              />
              <figcaption>
                {side === "original"
                  ? "Original profile · contacts redacted"
                  : "Reported profile · contacts redacted"}
              </figcaption>
            </figure>
          ))}
        </div>
      </div>
      {warnings.length > 0 && (
        <ul className="inspection-warnings">
          {[...new Set(warnings)].map((warning, i) => (
            <li key={i}>{englishText(warning)}</li>
          ))}
        </ul>
      )}
      <p className={pii ? "inspection-privacy warning" : "inspection-privacy"}>
        <b>
          Presidio:{" "}
          {pii
            ? `personal data regions found — ${pii}`
            : "no contact or financial identifiers detected"}
        </b>
        {pii > 0 && (
          <span>
            {" "}
            Types:{" "}
            {[
              ...new Set(
                [
                  ...inspection.original.privacy.findings,
                  ...inspection.suspect.privacy.findings,
                ].map((f) => f.entity_type),
              ),
            ].join(", ")}
            . Detected lines are covered with opaque masks in the images above.
          </span>
        )}
      </p>
      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={reviewed}
          onChange={(e) => onReview(e.target.checked)}
        />
        I have reviewed the extracted data
      </label>
      <small>
        OCR and duplicate detection can make mistakes. No warnings does not
        guarantee that no personal data remains. Check the masks and the
        screenshots. A moderator decides whether to add a label.
      </small>
    </section>
  );
}

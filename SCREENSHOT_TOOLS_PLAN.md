# Screenshot evidence tools

Goal: extract editable profile facts with PaddleOCR, find copied post photos with
imagededup, identify contact/financial PII with Presidio, and demonstrate a real
report through Meta + ML + human confirmation in the browser.

Scope: isolated Python 3.12 CPU worker on loopback; validated multipart inspection;
OCR field confidence and missing-data warnings; explicit user review; detection
of rectangular post-image regions and one-to-one perceptual-hash matches; privacy
warnings before sending screenshots to Meta; server-bound, expiring inspection
results attached to claims. Keep reviewer authentication and prior claims.

Non-goals: scrape Instagram, infer identity, guarantee all layouts/languages,
invent missing counts/booleans, train another model on demo examples, or confirm
claims automatically. Privacy findings are warnings; original evidence is retained.

Acceptance: real packages and actual screenshot inference, not mocked live output;
recognized text can be edited; blank/blurred inputs do not fabricate profiles;
avatar-only reuse is excluded from post-photo matches; unrelated photos are not
reported as duplicates; stale inspection IDs fail; raw PII is not logged or stored
in analysis summaries; found PII requires an explicit acknowledgement before Meta.
Existing manual reporting remains usable if the optional worker is unavailable.

Plan: dependency smoke tests -> failing parser/matcher/API tests -> worker and
inspection contract -> web autofill/preview/review -> full relevant checks ->
fresh browser walkthrough with real Meta and a persisted moderator label.

Completed 2026-11-03: claim d676e40c, 6 OCR fields per profile, 6 one-to-one
post-photo matches, 2 Presidio findings, real uncached Meta needs_review, both
ML models, human confirmation and confirmed label after browser reload.
All 7 earlier claims are unchanged. Verification: 116 backend + 6 vision +
3 privacy + 17 frontend tests, build/formatting and secret checks passed.
Evidence: outputs/browser-evidence-tools-20261103/verification.json and the
16-step /evidence-tools-walkthrough.html gallery.

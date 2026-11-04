# MirrorCheck — AI-Assisted Impersonation Review

Working hackathon submission draft. The owner reviews and submits the final form.

## One-line pitch

Turn suspected profile copies into reviewable evidence with Meta AI, local ML and human decisions.

## Main project description

A copied profile can look convincing long before anyone checks it. MirrorCheck turns suspected impersonation into evidence a human can review.

Inside an unofficial Instagram-style web prototype, a reporter uploads two profile screenshots. PaddleOCR extracts editable fields, imagededup and geometric feature matching look for reused photos, and local Presidio processing masks email and phone lines before Meta AI receives the images. The preview, provider-prepared image and saved reviewer evidence are checked for matching bytes.

Meta Muse Spark returns structured observations, differences, limitations and a recommendation. Separate local ML models estimate text reuse and auxiliary spam patterns. A default avatar cannot change the profile-model score by itself. No AI result adds a warning automatically.

A moderator must explain and explicitly confirm or dismiss the complaint. Version checks prevent stale decisions from overwriting newer reviews. Private history records the decision. A report-scoped, expiring appeal gives the affected party a way to explain context; the warning remains until a moderator upholds or overturns it.

We evaluated the new text model on 200 controlled test pairs derived from external professional bios, with source identities separated across splits: recall rose from 62% to 92%, with zero observed false positives among 100 negatives. On a separate Copydays photo-region challenge, recall rose from 2% to 36%, with zero observed false positives among 50 negatives. Difficult photo copies are still often missed. These research tasks do not establish real Instagram impersonation accuracy.

MirrorCheck runs locally and in a verified temporary US West Codespace with real Meta requests. Its public demo isolates visitors; the complete API report, moderator confirmation and appeal flow passed. The independent three-minute video is hosted on GitHub Pages. It does not connect to or modify Instagram, and screenshots cannot establish ownership.

## Compact description

MirrorCheck combines Meta Muse Spark, local ML, editable OCR, photo matching and contact redaction to review suspected profile copies. Explained moderator decisions, private history and scoped appeals keep humans responsible for warnings. Measured research challenges show improved recall; real Instagram accuracy remains unverified. The temporary public cloud flow has passed.

See `docs/INDEPENDENT_EVALUATION.md` for sources, confidence intervals and limits. Final form limits and eligibility must be checked in the organizer form. No claim of official Meta/Instagram affiliation is made.

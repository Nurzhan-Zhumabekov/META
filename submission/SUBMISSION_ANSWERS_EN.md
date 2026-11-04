# MirrorCheck вЂ” adaptable submission answers

Historical reusable answer blocks prepared on November 4, 2026. The current actual form is filled; see [FINAL_FORM_EN.md](FINAL_FORM_EN.md) for its exact draft and submission state. Older test counts and hosting notes below describe the earlier preparation.

Project name: **MirrorCheck вЂ” AI-Assisted Impersonation Review**

Tagline: Turn suspected profile copies into reviewable evidence with Meta AI, local ML and contact redaction.

Main and shorter descriptions: [PROJECT_DESCRIPTION_EN.md](PROJECT_DESCRIPTION_EN.md).

## Problem and intended users (55 words)

Creators and ordinary users need a clear way to document a profile that appears to copy their identity. Reviewers need comparable evidence, visible uncertainty and a deliberate decision step. MirrorCheck targets that reporting and review workflow. It is a prototype of a potential social-platform feature, with no claim of user adoption or measured time savings.

## What the project does (63 words)

A reporter supplies screenshots of the original and suspected copy. Editable OCR fields, image-region matches and masked previews help prepare the evidence. Meta AI provides structured visual observations; two local ML models provide separate text-reuse and profile-pattern signals. The report remains under review until a moderator takes an explicit action. Confirming the fictional case adds a warning that remains after reloading the profile.

## How Meta AI is used (70 words)

The backend calls the Meta Model API with muse-spark-1.3, using the English prompt version impersonation-evidence-v2-en. It sends processed profile screenshots, validates structured results and presents similarities, differences, limitations and a constrained recommendation. The API key stays on the server. This is visual evidence analysis rather than identity verification: Meta's recommendation cannot directly confirm a report. The demonstrated response is real and uncached; no Meta model was fine-tuned for this project.

## Why Meta AI is central to the project (61 words)

Meta Muse Spark adds a visual comparison that the numeric profile classifier cannot provide. It can describe reused biography text, avatar graphics, highlights and post grids together with meaningful differences and screenshot limitations. Local ML remains visible as independent evidence instead of being presented as a second opinion on identity. This makes the model output usable within a moderator's review process.

## How it is built (72 words)

The application uses React, TypeScript and Vite, served with a same-origin FastAPI backend. Authenticated local workers run PaddleOCR, imagededup and Presidio. The provider boundary enforces image redaction; processed images are stored for authorized reviewer access. Logistic-regression inference uses JSON artifacts for the profile and pair models. Claims and moderator decisions persist in local JSON storage. The current storage and operational setup are suitable for a single-writer demonstration, not a production moderation service.

## What is distinctive (66 words)

The contribution is the complete evidence workflow: editable extraction, image reuse signals, contact masking before the external visual model, structured Meta observations, independent ML and a separate moderator transition. The reviewer can inspect the same processed images used for Meta analysis. The profile model deliberately excludes avatar presence, and the interface discloses the pair model's synthetic training data. These are implemented behaviors rather than promised features.

## Privacy, safety and decision boundaries (81 words)

A local OCR and Presidio pipeline identifies contact lines and covers them with padded opaque masks before provider image submission. Failed processing blocks the request. The demo verifies equality between preview, provider-prepared and reviewer-stored JPEG bytes, with no EXIF metadata in those processed images. Detection is imperfect: this is protection for detected identifiers, not a promise of complete anonymization. Reviewer evidence requires authentication. No screenshot or model score proves account ownership; the separate moderator action is demonstrated only on fictional accounts.

## Challenges and tradeoffs (68 words)

OCR can confuse handles, display names and biography lines, so the report form requires review and correction. A historical fake/spam classifier also answers a different question from copied-profile detection; the project separates those signals and adds a text-reuse pair model. Excluding avatar presence guarantees avatar invariance, but did not improve every metric on the older spam holdout. The synthetic pair model and screenshot-based evidence still require external validation.

## Current accomplishments and validation (81 words)

The English browser walkthrough records a complete fictional report, local inspection and contact masking, an uncached Meta Muse Spark response, local ML results, an under-review state, a moderator confirmation and a profile warning that persists after reload. Two example contact regions were masked; a second local OCR/Presidio scan found zero remaining detected identifier regions in those processed demo images. The most recent recorded full test run passed 123 backend and 24 frontend tests. These are development checks, not real-world accuracy measurements.

## Next steps (67 words)

First, build a consented, independently labelled evaluation set that includes legitimate look-alikes, fan and parody accounts, sparse profiles, changed usernames, image crops and OCR failures. Measure false positives and recall separately for copy detection and spam patterns. Then add verified ownership evidence, appeals, audit logs, database-backed concurrency, abuse controls, monitoring and a clearly defined deployment model. Any real Instagram integration would require a separate authorized integration path.

## Open-source components and attribution (79 words)

PaddleOCR extracts text; imagededup compares image regions; Microsoft Presidio detects contact information for local masking; scikit-learn is used for training logistic-regression models; React, Vite and FastAPI power the web application. Embla Carousel and emoji-picker-react support the social interface. This source release includes two JSON inference artifacts and setup instructions. MIT covers original project code, with separate third-party and media notices. Raw historical training CSVs are not redistributed; the mirrored dataset's provenance and transformations still require review before other redistribution.

## Builder bio / team field draft (42 words)

Nurzhan Zhumabekov is a Software Engineering student at Astana IT University in Astana, Kazakhstan, building web applications and AI-assisted tools. His public GitHub profile is https://github.com/Nurzhan-Zhumabekov. Confirm the complete team roster and each person's contribution before submitting any team or authorship fields.

## Links and owner-only fields

| Item | Verified status / required action |
| --- | --- |
| GitHub | https://github.com/Nurzhan-Zhumabekov/META вЂ” this source release includes the web application, legacy client, tests, JSON models and an MIT license for original code. Check `REPOSITORY_PUBLICATION.json` when present for the application commit verified after upload. |
| Demo video URL | [Finished 03:00 English MP4](https://github.com/Nurzhan-Zhumabekov/META/raw/refs/heads/main/web/public/MirrorCheck_Demo_EN_3min.mp4). Check the actual form's accepted video hosts before using a repository MP4 URL. |
| Public application URL | Not verified or prepared here. `localhost:8090` is accessible only on the development machine. Do not paste it as a public demo URL. |
| Track | Indie developer is recommended for a student/individual entry; confirm the actual registration. |
| Theme | Build for Your World is recommended. |
| Team members / contributions | Owner to verify. Do not invent additional contributors or claim sole authorship without checking. |
| Eligibility / agreements | Owner to read the actual terms and answer personally. This packet makes no eligibility attestations. |
| Submission destination | [Cerebral Valley submission form](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit). Authentication is needed to verify the final questions and limits. |

Finished video and its newer fictional case: [VIDEO_DELIVERY_EN.md](VIDEO_DELIVERY_EN.md). The original script and stills describe the earlier archive-profile run.

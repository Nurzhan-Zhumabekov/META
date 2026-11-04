# MirrorCheck — final Cerebral Valley form draft

Prepared from the actual form on 5 November 2026. Not submitted yet; promotional-use consent and personal survey answers await the owner's confirmation.

Team: beyond
Member shown: Nurzhan_Zhuma / Nurzhan Zhumabekov
Track: Indie Developer Track
Theme: Build for Your World
Repository: https://github.com/Nurzhan-Zhumabekov/META
Video: https://nurzhan-zhumabekov.github.io/META/
Live demo: https://congenial-garbanzo-4j5v4xwwx9r3jw9v-8090.app.github.dev/demo-guide.html

## Project Description

MirrorCheck — AI-Assisted Impersonation Review

MirrorCheck turns a suspected copied social profile into evidence a human can review. Creators and ordinary users can report an apparent account copy from an Instagram-style web interface, attach original and suspected-profile screenshots, and follow the decision through to a visible profile warning.

PaddleOCR extracts editable account fields; imagededup finds reused photo regions. A local OCR + Microsoft Presidio pipeline masks detected email and phone regions before any screenshot reaches Meta. Failed redaction blocks external analysis. Meta Muse Spark 1.3 returns structured visual similarities, differences, limitations and a constrained recommendation. Separate local models show profile-pattern and pair text-reuse signals. A standard avatar is excluded from the profile model's features.

AI cannot add a warning. A moderator must inspect the processed evidence and record an explained decision. Confirmed reports display a warning; dismissed reports do not. Version 0.13 adds audit history, report-scoped appeals, SQLite persistence and isolated visitor sandboxes.

Built with React, TypeScript, Vite and FastAPI, with authenticated local workers and server-side Meta credentials. The public demo runs the real API and local ML in a US West Codespace. Each visitor gets a fictional sandbox; only the web port is public. A built-in example pair supports the full review without uploading private files. Live demo: https://congenial-garbanzo-4j5v4xwwx9r3jw9v-8090.app.github.dev/demo-guide.html

Evaluation separates copy detection from spam patterns. Controlled external-text copy recall improved from 62/100 to 92/100; a difficult Copydays photo-region test improved from 1/50 to 18/50. These are component evaluations, not real Instagram impersonation accuracy. Pair-model training is synthetic; no screenshot or score establishes ownership.

This is an unofficial feature prototype, not an integration with the real Instagram service. The recorded three-minute English demo uses fictional accounts, edited authentic browser captures and synthesized narration. Codespaces is temporary attended hosting; the independently hosted video remains available when the live app sleeps. Source, model artifacts, evaluation methods and third-party notices are public. Future work includes consented account-level validation and verified ownership evidence. Evaluation sources and limitations are documented in the repository. No raw external profiles are redistributed.

## Describe your use of Meta products to build the submitted project

The backend calls the Meta Model API with muse-spark-1.3 through Chat Completions. It supplies two locally processed screenshots and an English developer prompt (impersonation-evidence-v2-en), requests a strict JSON schema, validates the response and presents visual similarities, differences, uncertainty and a constrained recommendation alongside separate local ML signals.

Before provider submission, PaddleOCR and Microsoft Presidio identify contact lines and replace detected email/phone regions with padded opaque masks. Processing failure blocks the request. The moderator can inspect the same processed image bytes supplied to Meta. This protects detected identifiers, not every possible personal detail.

The key remains in server-side, repository-scoped Codespaces secrets. The public app uses signed isolated visitor sessions, authenticated local workers, input limits and Meta request budgets. Readiness checks query the real model catalog rather than treating a configured key as proof of access; provider failures are surfaced without creating a false result.

Meta's output does not directly confirm or reject a claim. An explicit moderator decision is required, with an explanation and audit history; scoped appeals can overturn it. We use no Meta fine-tuning and do not claim use of Muse Code, Muse Wonder, Muse Image or SAM 3.1. The project is a standalone unofficial Instagram-style prototype.

## Why are Meta's models important to your solution?

Muse Spark adds visual evidence comparison that our numeric profile classifier cannot provide. It can discuss matching avatars, biography text, highlight graphics and post-grid content together with visible differences and screenshot limitations. This complements OCR, perceptual photo matching and two narrowly scoped ML signals without presenting any of them as proof of identity.

Structured output makes the comparison usable in a review interface: observations and limitations are validated, displayed with processed evidence and kept separate from the moderator's decision. This supports a complete report-to-review workflow rather than a single opaque fake-account score.

We tested the real endpoint and distinguish live responses from cached results. Cloud access initially returned an empty model catalog and model_not_found in the first Codespace; the same key and model worked in the replacement US West environment. We report that observed difference without claiming a diagnosed regional policy or a general vendor outage. Production use would still require independent account-level validation, operational monitoring and verified ownership evidence. We have not run a controlled comparison against other multimodal providers. Not every model recommendation will be correct, which is why the human review and appeal steps are essential.

## Survey values currently in the draft

- Likelihood to build with Meta API: Very likely (form default; owner to confirm).
- Overall opinion: Very favorable (form default; owner to confirm).
- Recommend Meta API: 5/5 (form default; owner to confirm).
- Recommend Muse Code: 5/5 (form default; owner to confirm; this project does not claim use of Muse Code).
- Biggest obstacle: Errors / outages or unreliable service.
- Comparative performance: We've used other models but couldn't make a clear comparison.
- Most important: Quality of the answers and code (owner to confirm).
- Switching: Our product is tuned to our current model’s behavior and prompts (owner to confirm).
- Production blocker: Reliability or uptime.

Optional X post and partner-technology feedback are blank.

The form includes a preselected promotional-use consent: Meta and Cerebral Valley may use, publish, share and promote submitted materials on their websites, social media and marketing channels. A preselected checkbox is not treated as the owner's consent.

# Facts and sources for the submission

Prepared November 4, 2026. Project evidence below comes from already-recorded verification files, not a new full test run or a fresh Meta request during document preparation.

## Verified fictional run

Source: `outputs/browser-english-flow-20261104/verification.json`, verified at `2026-11-04T15:42:12.580200+00:00`. A minimal copy of the relevant facts is provided in [VERIFIED_DEMO_FACTS.json](VERIFIED_DEMO_FACTS.json).

| Claim | Supported wording | Limit |
| --- | --- | --- |
| Real Meta use | Meta Model API, `muse-spark-1.3`, uncached response, recommendation `needs_review` | Not a new call made for this packet; no fine-tuning claim |
| Demo accounts | Fictional `aigerim.k` and `aigerim.k.archive` | Not real Instagram accounts or a real identity investigation |
| Combined similarity | 85.85% | A comparison signal for one input, not measured accuracy |
| Pair text-reuse ML | 72.19% | Synthetic pair training; real-world performance unvalidated |
| Auxiliary profile ML | 94.46% | Historical fake/spam patterns; not an impersonation probability |
| Image deduplication | 1 matching grid region | Not six independently matched photo regions in this run |
| Redaction | 2 detected contact regions masked | Detected identifiers only; no blanket anonymity guarantee |
| Second local scan | 0 remaining detected identifier regions in the processed demo images | Detector-dependent, not proof that every possible identifier is absent |
| Evidence consistency | Preview, provider-prepared and stored JPEG bytes match | Processing integrity, not identity authenticity |
| Unauthenticated evidence request | HTTP 401 | Limited demonstrated check, not a complete security audit |
| Decision and persistence | `under_review` → separate moderator action → `confirmed`, warning survives reload | Operator played both roles in the fictional demonstration |
| OCR | Editable fields reviewed and corrected against screenshots | Do not claim perfect automatic extraction |

The application rounds the three result cards to 86%, 72% and 94%. Exact evidence values above are available for a clearly labelled editor overlay, if needed.

## Tests and ML context

- Latest recorded full suite: **123 backend + 24 frontend = 147 passing tests**, recorded in `outputs/english-ui/verification.json`. The subsequent English browser-run record includes a successful web build, English-copy test and formatting check. No full suite was rerun merely to write these documents.
- `profile-logreg-v2-no-avatar` excludes avatar presence from both fitting and inference. Toggling only that flag leaves its score unchanged. This does not guarantee a legitimate profile can never receive a high score for other inputs.
- `pair-text-logreg-v1-synthetic` uses 3,120 fictional training pairs, 780 validation pairs and 780 test pairs. Shared generator structure and feature overlap limit the holdout's independence. Avoid general-accuracy claims from those results.
- A prior 15-case development suite exercised real Meta responses with the earlier profile model. The later v2 comparison replayed those saved Meta answers; it was not 15 new live v2 calls. Do not mix those evaluations with the latest fictional demo.
- The profile v2 older 118-profile holdout accuracy was 88.98%, lower than v1's 91.53%; removing avatar presence is a deliberate invariance tradeoff. These older spam-task metrics are not account-copy detection performance and are intentionally absent from the pitch.
- ML and dataset details: `ML_INTEGRATION.md`, `ML_V2_PLAN.md`, `EVAL_PLAN.md`; inference artifacts and reports are under ignored `outputs/ml/`.
- Upstream dataset/project reference: [Detection of Fake Accounts in Social Media](https://github.com/Ajaysagayam/Detection_of_Fake_Accounts_in_Social_Media). The project's own training and inference pipeline is separate. Raw mirror provenance and transformation rights need review before source/data distribution.

## Implemented versus future work

Implemented: native English web UI; editable screenshot extraction; local image-region comparison; detected email/phone masking before provider images; structured Meta analysis; separate local ML; authenticated review; persisted local report decisions.

Future / unverified: official Instagram integration, live account import, proof of account ownership, independent human validation of real cases, calibrated impersonation probabilities, production scalability, concurrent database storage, measured user impact, appeals and public deployment. Source publication and clean-checkout verification are recorded separately in `REPOSITORY_PUBLICATION.json`, when present.

## Submission requirements and external sources

- [Meta official hackathon page](https://dev.meta.ai/events/global-hackathon): deadline November 4 at 9 PM ET, tracks and themes. Checked during preparation. For November 4, 2026, US Eastern is UTC−5; Astana is UTC+5, giving November 5 at 07:00 Astana.
- [Cerebral Valley event page](https://cerebralvalley.ai/e/meta-ai-developer-hackathon): event context and key dates. Application-selection guidance must not be represented as an unseen final-project rubric.
- Organizer reminder dated November 3, 2026 UTC: three-minute demo guidance; mandatory open-source GitHub repository. Private message contents and headers are not bundled.
- [Submission form](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit): sign-in was required to inspect the actual final fields. Exact limits and upload rules are unverified here.
- [Project GitHub repository](https://github.com/Nurzhan-Zhumabekov/META): initially public and empty when the packet was first prepared. The source release adds implementation and license; `REPOSITORY_PUBLICATION.json`, when present, records the actual application commit and checks verified after upload.

## Language to avoid

Avoid: “official Instagram feature”, “100% detection”, “proves who owns the account”, “fully anonymous”, “all data stay local”, “94% accurate”, “six imagededup photo matches” for this run, “independent moderator verified a real account”, “live demo” for a still-image replay, “production ready”, “published open-source implementation” while the repository is empty.

Use the concrete implemented behavior and its scope instead. The completed video is distributed as a source-release MP4; acceptance of that host in the final form remains unverified. Final hackathon submission is unfinished. Source publication is a separate verified action when documented in `REPOSITORY_PUBLICATION.json`.

Finished video and its newer fictional case: [VIDEO_DELIVERY_EN.md](VIDEO_DELIVERY_EN.md). The original script and stills describe the earlier archive-profile run.

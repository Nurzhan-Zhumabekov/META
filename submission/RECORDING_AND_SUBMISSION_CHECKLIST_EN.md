# Recording and submission checklist

## Current state

Prepared: English description variants, adaptable answer blocks, a 180-second edit plan, exact voiceover text, draft SRT captions, and 15 real browser stills from the fictional English run.

This packet is distributed with the application source, bundled JSON models, setup instructions and an MIT license for original code. No finished narrated video, video hosting, public application deployment or final hackathon submission is included. `REPOSITORY_PUBLICATION.json`, when present, records verified source publication separately.

## Deadline and source of the requirements

- Published project deadline: **November 4, 2026 at 9:00 PM US Eastern (EST, UTC−5)**.
- Same instant: **November 5, 2026 at 02:00 UTC / 07:00 in Astana (UTC+5)**.
- [Official Meta event page](https://dev.meta.ai/events/global-hackathon) and [Cerebral Valley event page](https://cerebralvalley.ai/e/meta-ai-developer-hackathon) publish the deadline. Dates may change; check the live form before final submission.
- Organizer email dated November 3, 2026 UTC calls for a **three-minute demo video** and says an **open-source GitHub repository is mandatory**. This packet does not reproduce private email headers or contact details.
- The authenticated [submission form](https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit) was not readable in this session. No exact field limits, video-host restrictions or other unseen requirements are asserted.

## 1. Prepare the recording

- [ ] Open [the existing English walkthrough](http://localhost:8090/english-report-walkthrough.html). It has 15 actual captures in chronological order.
- [ ] Open [the saved labelled profile](http://localhost:8090/profile/aigerim.k.archive). Use only the fictional `aigerim.k` / `aigerim.k.archive` case in the video.
- [ ] Read [DEMO_VIDEO_SCRIPT_EN.md](DEMO_VIDEO_SCRIPT_EN.md); record [VOICEOVER_EN.txt](VOICEOVER_EN.txt) at the provided pace.
- [ ] Assemble the provided stills into the timed sequence, or screen-record the actual walkthrough and the labelled profile. Keep replay and condensed-wait disclosures visible.
- [ ] Use source captures for the already-completed moderator action. A fresh live action would require a new fictional report; it is not needed for this recording.
- [ ] Add the project title as an editor overlay. The application still uses its existing concept name.
- [ ] Check that example contact details and public fictional handles are the only identifiers shown. Do not expose reviewer credentials, server secrets or unrelated report details.
- [ ] Retiming: align SRT cues with the actual spoken words. Export a video of no more than three minutes for this plan. Check the actual form in case it specifies a different hard limit or format.
- [ ] Play the entire final export once with audio and captions. Confirm report → redaction → Meta + ML → under review → moderator → persistent warning are all visible and readable.

## 2. Complete the mandatory open-source repository

Repository: https://github.com/Nurzhan-Zhumabekov/META. This release supplies the implementation and MIT license for original code. See `REPOSITORY_PUBLICATION.json`, when present, for a verified uploaded application commit. Keep these checks when preparing a later update.

- [x] Publish the current native web frontend, backend, local workers, tests, scripts, dependency manifests and setup documentation.
- [x] Add an appropriate license for code the owner has the right to license; preserve third-party notices and media credits. Public visibility alone does not provide an open-source license.
- [x] Exclude `.env`, worker/reviewer keys, logs, raw reports, private evidence, caches, virtual environments and `node_modules`. Do not upload the entire `outputs/` directory.
- [x] Both JSON inference models are bundled in `models/`; the installer and clean-clone inference were verified. Runtime copies stay under ignored `outputs/ml/`.
- [x] The screenshot workers require additional environments/models. Document their setup and initial downloads, not only the web launcher. A server Meta API key is required for live external analysis.
- [ ] Review the provenance and redistribution terms of the historical profile dataset and derived assets. Do not automatically bundle mirrored raw CSVs. Keep ML limitations visible.
- [x] Include a small explicitly fictional sample case and a safe walkthrough. Do not include real complaint records or organizer mail.
- [x] Test the exact public commit from a clean checkout. Confirm installation, web build, worker readiness and whether inference artifacts are present. Existing local tests are not proof of a reproducible public release.
- [x] Open the repository while signed out. Verify code, license, README, setup and demo/video links are accessible.

## 3. Upload the video and fill the form

- [ ] Upload the finished video to a host allowed by the actual form; use a viewing URL that works without requesting account access. No host is assumed in this packet.
- [ ] Confirm the actual project title, registered track, team roster and individual contributions. Recommended positioning: Indie developer / Build for Your World, subject to eligibility and registration.
- [ ] Paste the main or shorter description from [PROJECT_DESCRIPTION_EN.md](PROJECT_DESCRIPTION_EN.md), fitting the actual field limits.
- [ ] Adapt relevant blocks from [SUBMISSION_ANSWERS_EN.md](SUBMISSION_ANSWERS_EN.md). They are not a verified list of final form questions.
- [ ] Replace missing video/public-demo fields with real links. `localhost:8090` cannot be visited by judges on another computer; do not submit it as the public product URL.
- [ ] If a public deployment is required, prepare a protected demonstration deployment separately. Do not expose the current moderator surface or development server to the internet as a shortcut.
- [ ] Review eligibility statements, official rules and any agreements personally. This packet does not attest to eligibility or accept terms.
- [ ] Submit the final form before the deadline, then save the confirmation page or receipt and the submitted links.

## Final check before submission

The story should be: **a working AI-assisted evidence and moderation feature**, with a clear Meta model contribution, privacy handling and an explicit decision boundary. Keep future work separate from implemented functionality. State that this is an unofficial local prototype and that real-world copy-detection performance is not established.

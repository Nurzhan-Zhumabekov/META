# MirrorCheck — three-minute demo-video script

Target runtime: **03:00 maximum for this edit plan**, matching the organizer's three-minute demo guidance. The exact form's upload restrictions were not visible; check them before upload.

Voiceover: **322 words**, approximately 107 words per minute across the full video. Individual scenes leave room for visual pauses. Read in a calm, conversational voice; no need to read handles, percentages or implementation versions aloud.

Format: 1920 × 1080 landscape is an editing recommendation, not a verified organizer requirement. Use 1080p legible crops, a clean English interface, and an audible English voiceover.

This script uses the **real recorded run** of fictional claim `5828394c`, verified November 4, 2026. Captures are supplied in [stills/](stills/). They are already-recorded evidence, not a new live Meta request. Keep the lower-third **Recorded real browser run · Fictional accounts** visible during the replay; label condensed processing time. This packet contains no finished video or recorded audio.

The current demo claim is already confirmed. Use its earlier real captures for the before/under-review stages; do not reset stored reports to stage a new transition. The operator played both reporter and moderator in this fictional demonstration.


## 00:00–00:12 · 1. The problem

**Screen / edit:** Open on a simple title card: MirrorCheck / AI-Assisted Impersonation Review. Cut to the original and the suspected copy side by side. Keep the usernames legible.

**Source captures:** [01-original-profile.png](stills/01-original-profile.png), [02-copy-before-report.png](stills/02-copy-before-report.png)

**On-screen text:** Unofficial Instagram-style prototype · Fictional accounts

**Say:**

> An impersonator can copy a creator's photos and biography while changing just the username. MirrorCheck helps turn that suspicion into evidence a reviewer can inspect.


## 00:12–00:28 · 2. Show the working product

**Screen / edit:** Identify aigerim.k and aigerim.k.archive. Point to the shared display name, bio, avatar graphic and gallery. Show that the copy initially has no warning.

**Source captures:** [01-original-profile.png](stills/01-original-profile.png), [02-copy-before-report.png](stills/02-copy-before-report.png)

**On-screen text:** Recorded real browser run · No real accounts reported

**Say:**

> This is our working, unofficial Instagram-style web prototype. These two fictional accounts share a name, biography, avatar and post images, but have different usernames.


## 00:28–00:50 · 3. Report and review OCR

**Screen / edit:** Show Report account → Pretending to be someone else. Then show the screenshot-upload and OCR captures. Zoom the reviewed fields and I have reviewed the extracted data. Explain the corrections without pretending extraction was perfect.

**Source captures:** [03-report-reason.png](stills/03-report-reason.png), [04-ocr-processing.png](stills/04-ocr-processing.png), [06-reviewed-ml-fields.png](stills/06-reviewed-ml-fields.png)

**On-screen text:** PaddleOCR → editable fields → reporter review

**Say:**

> From the suspected copy, I choose Report account, then Pretending to be someone else. I attach screenshots of the original and suspected profile. PaddleOCR fills editable fields, and I correct the extracted text against the screenshots before submitting.


## 00:50–01:12 · 4. Privacy before the provider

**Screen / edit:** Hold on the suspect preview with the email and phone lines masked. Show a small editor-added flow: local OCR + Presidio → processed JPEG → Meta AI. Add an editor-added verification note, clearly separate from the application UI: 2 regions masked; preview/provider-prepared/stored bytes match.

**Source captures:** [05-ocr-redaction-preview.png](stills/05-ocr-redaction-preview.png)

**On-screen text:** Detected contact lines masked locally before Meta AI

**Say:**

> Before any image reaches Meta AI, Presidio identifies the example email and phone. The server permanently covers both contact lines. These previews are the actual processed images prepared for Meta, with matching hashes for the evidence saved for review.


## 01:12–01:36 · 5. Real Meta Muse Spark analysis

**Screen / edit:** Show processing, then the receipt and Meta AI summary in 09-meta-and-ml-results.png. Zoom the actual English reuse observations and ownership limitation. The supplied capture does not expose the model-version field: put muse-spark-1.3 and needs_review in a clearly editor-added caption, sourced from VERIFIED_DEMO_FACTS.json. The moderator capture shows the processed evidence images. Do not show a reviewer access code.

**Source captures:** [07-meta-processing.png](stills/07-meta-processing.png), [08-report-receipt.png](stills/08-report-receipt.png), [09-meta-and-ml-results.png](stills/09-meta-and-ml-results.png), [11-moderator-evidence.png](stills/11-moderator-evidence.png)

**On-screen text:** Real uncached Meta response · needs_review · Waiting time condensed

**Say:**

> Meta Muse Spark analyzes the processed screenshots through our backend and returns structured similarities, differences and limitations. Here it identifies reused profile content and recommends further review. It explicitly says screenshots cannot establish ownership. This is a real API response from the recorded run.


## 01:36–01:56 · 6. Independent ML and image evidence

**Screen / edit:** Show Content reuse signals · ML, Image and name similarity and Spam patterns · ML separately. Application cards round to 72%, 86% and 94%. If adding an editor overlay with more precision, use 72.19%, 85.85% and 94.46%. Describe the imagededup result as ONE matching grid region, not six individual photo detections.

**Source captures:** [09-meta-and-ml-results.png](stills/09-meta-and-ml-results.png), [11-moderator-evidence.png](stills/11-moderator-evidence.png)

**On-screen text:** Text reuse ≠ spam patterns ≠ identity verification

**Say:**

> Local models add separate signals: a text-reuse comparison between the two profiles, and an auxiliary profile spam-pattern score. Image deduplication also finds a matching grid region. These scores are evidence signals, not accuracy claims or proof of identity.


## 01:56–02:14 · 7. Keep uncertainty visible

**Screen / edit:** Show Account under review, then the synthetic-training disclosure in the analysis. Add a small editor note: profile model excludes avatar presence. Do not suggest the demo proves every ordinary profile is safe or that an actual avatar was changed during this run.

**Source captures:** [10-profile-under-review.png](stills/10-profile-under-review.png), [09-meta-and-ml-results.png](stills/09-meta-and-ml-results.png)

**On-screen text:** Under review · Synthetic pair training disclosed

**Say:**

> The report remains Under review. Our profile model excludes avatar presence, so changing only a default-avatar flag cannot change its score. The pair model uses synthetic training data, a limitation shown to the reviewer.


## 02:14–02:32 · 8. Separate moderator decision

**Screen / edit:** Show the relevant claim's processed evidence, then the Decision saved capture. The supplied 12-moderator-decision.png is cropped to evidence; the action button and click are outside the capture. Describe Confirm impersonation through narration and an editor-added caption, not a fabricated button or click. This is a replay of the authorized fictional demo, where the operator also played the moderator; it is not an independent identity investigation.

**Source captures:** [11-moderator-evidence.png](stills/11-moderator-evidence.png), [12-moderator-decision.png](stills/12-moderator-decision.png), [13-decision-saved.png](stills/13-decision-saved.png)

**On-screen text:** Moderator action required · Fictional demonstration

**Say:**

> In the moderator view, I inspect the processed images and analysis, then explicitly select Confirm impersonation for this fictional case. The AI recommendation alone cannot perform this transition.


## 02:32–02:50 · 9. Warning and persistence

**Screen / edit:** Hold on Impersonation confirmed. Cut to the after-reload capture. If recording the live labelled page now, reload it and show the saved warning; do not reset the existing report to recreate the earlier state.

**Source captures:** [14-profile-labelled.png](stills/14-profile-labelled.png), [15-label-after-reload.png](stills/15-label-after-reload.png)

**On-screen text:** Impersonation confirmed · Persists after reload

**Say:**

> The profile now displays Impersonation confirmed. Reloading preserves the warning because the decision is stored on the server. This demonstrates the complete report-to-review workflow; it does not modify the real Instagram service.


## 02:50–03:00 · 10. Close with the value and next step

**Screen / edit:** End on MirrorCheck, the one-line value proposition and Meta Muse Spark + local evidence + moderator review. Add the repository URL only after it contains the current source and license. End at 03:00 or earlier.

**Source captures:** [15-label-after-reload.png](stills/15-label-after-reload.png)

**On-screen text:** Review suspected copies. Reduce contact exposure. Keep a moderator in control.

**Say:**

> MirrorCheck makes suspicious copies easier to review while reducing contact exposure. Next, we need consented real-world evaluation and production hardening.


## Notes for the edit

- Preserve the English labels: `Report account`, `Pretending to be someone else`, `I have reviewed the extracted data`, `Under review`, `Confirm impersonation`, `Impersonation confirmed`.
- Put editor-added titles, diagrams and precision metrics on a clearly separate overlay; do not paint new controls or observations into the application capture.
- The actual application rounds the result cards. Exact evidence values are combined similarity 85.85%, pair text reuse 72.19%, profile spam patterns 94.46%. These are three different signals, not three accuracy measurements.
- imagededup matched one grid region in this run. Meta observed reuse across the first six gallery images. Those statements are different and must not be combined into a claim of six separate imagededup matches.
- The redaction scan found zero remaining *detected* identifier regions in these processed demo images. Do not say that every identifier is always removed or that all user data stay local: the processed screenshots go to Meta.
- Do not record server consoles, `.env`, access codes, unrelated claims, email tabs, API dashboards or billing screens.
- The existing moderator stills show evidence and the saved-decision receipt, not the actual button click. Narrate that transition over an editor caption. If continuous click footage is required, it must be recorded separately with another explicitly fictional case; do not reset this completed report or invent click footage.
- `CAPTIONS_EN.srt` is timed to this plan, not to a recording. Retiming against the finished narration is required before export.
- Existing image and component attributions are copied into [EXISTING_PHOTO_CREDITS.html](EXISTING_PHOTO_CREDITS.html) and [EXISTING_COMPONENT_NOTICES.txt](EXISTING_COMPONENT_NOTICES.txt), without relicensing. The existing photo-credits page concerns the football media expansion; it is not an exhaustive provenance audit of every earlier stock image visible in the prototype. Keep applicable notices and verify the media used in the final export before public distribution.

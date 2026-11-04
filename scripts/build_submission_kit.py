"""Build English submission copy and a three-minute edit plan from verified evidence.

Writes local documents and copies the existing fictional demo stills only.
Never submits a form, publishes source, changes claims, or calls an AI provider.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import shutil
import textwrap
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from dotenv import dotenv_values

ROOT = Path(__file__).resolve().parents[1]
KIT = ROOT / "submission"
DEMO = ROOT / "outputs/browser-english-flow-20261104"
ARCHIVE = ROOT / "outputs/submission-kit-20261104.zip"
TITLE = "MirrorCheck"
SUBTITLE = "AI-Assisted Impersonation Review"
TAGLINE = "Turn suspected profile copies into reviewable evidence with Meta AI, local ML and contact redaction."
REPO = "https://github.com/Nurzhan-Zhumabekov/META"
FORM = "https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit"
OFFICIAL = "https://dev.meta.ai/events/global-hackathon"

DESCRIPTION = """A copied profile can look convincing long before anyone checks it. MirrorCheck helps users document suspected impersonation and gives reviewers a structured path from complaint to decision.

Built as an unofficial Instagram-style web prototype, it starts inside the profile flow. A reporter attaches screenshots of the original and suspected copy. PaddleOCR extracts editable profile fields, while imagededup flags matching image regions. The reporter reviews and corrects the extracted data before submitting.

Before screenshots reach Meta AI, a local Presidio pipeline detects email and phone lines and covers them with opaque masks. The preview, provider-prepared image and stored reviewer evidence are checked for matching bytes. Processing failures block the external image request.

Meta Muse Spark, accessed through the backend with muse-spark-1.3, compares the processed screenshots and returns structured similarities, differences, limitations and a review recommendation. Two local ML models add separate signals: text reuse between profiles and auxiliary spam patterns in profile statistics. Avatar presence is excluded from the profile model, so an ordinary default avatar cannot change that model's score by itself.

The report stays under review until a separate moderator action. In the completed fictional demo, the moderator confirms impersonation and the profile warning persists after a reload. The English interface demonstrates the whole journey in context.

MirrorCheck is a working local prototype, with a real Meta API run and a recorded end-to-end browser walkthrough. It does not connect to or modify the real Instagram service. Screenshots and model scores cannot establish ownership; the pair model uses synthetic training data, and performance on real account-copy cases remains unvalidated. The next step is consented evaluation and production hardening."""

SHORT_DESCRIPTION = """MirrorCheck is an unofficial Instagram-style web prototype for reporting suspected profile copies. Users attach two screenshots, review PaddleOCR fields, inspect image matches and preview contact details masked locally with Presidio before Meta AI receives images. Meta Muse Spark returns structured visual evidence; local ML adds separate text-reuse and profile spam-pattern signals. A moderator reviews the evidence and explicitly decides whether to add a persistent profile warning. A real Meta API run demonstrates the complete workflow with fictional accounts. The prototype does not modify Instagram, and its scores do not prove ownership. Real-world copy-detection performance still requires evaluation."""

VERY_SHORT = """MirrorCheck combines Meta Muse Spark, editable OCR, image deduplication and local contact redaction to help review suspected profile copies. Reports stay under review until a separate moderator decision adds a persistent warning. The working Instagram-style web demo uses fictional accounts; it does not modify Instagram or establish ownership."""

ANSWERS = {
    "problem_and_users": "Creators and ordinary users need a clear way to document a profile that appears to copy their identity. Reviewers need comparable evidence, visible uncertainty and a deliberate decision step. MirrorCheck targets that reporting and review workflow. It is a prototype of a potential social-platform feature, with no claim of user adoption or measured time savings.",
    "solution_and_workflow": "A reporter supplies screenshots of the original and suspected copy. Editable OCR fields, image-region matches and masked previews help prepare the evidence. Meta AI provides structured visual observations; two local ML models provide separate text-reuse and profile-pattern signals. The report remains under review until a moderator takes an explicit action. Confirming the fictional case adds a warning that remains after reloading the profile.",
    "meta_model_usage": "The backend calls the Meta Model API with muse-spark-1.3, using the English prompt version impersonation-evidence-v2-en. It sends processed profile screenshots, validates structured results and presents similarities, differences, limitations and a constrained recommendation. The API key stays on the server. This is visual evidence analysis rather than identity verification: Meta's recommendation cannot directly confirm a report. The demonstrated response is real and uncached; no Meta model was fine-tuned for this project.",
    "why_meta_matters": "Meta Muse Spark adds a visual comparison that the numeric profile classifier cannot provide. It can describe reused biography text, avatar graphics, highlights and post grids together with meaningful differences and screenshot limitations. Local ML remains visible as independent evidence instead of being presented as a second opinion on identity. This makes the model output usable within a moderator's review process.",
    "technical_implementation": "The application uses React, TypeScript and Vite, served with a same-origin FastAPI backend. Authenticated local workers run PaddleOCR, imagededup and Presidio. The provider boundary enforces image redaction; processed images are stored for authorized reviewer access. Logistic-regression inference uses JSON artifacts for the profile and pair models. Claims and moderator decisions persist in local JSON storage. The current storage and operational setup are suitable for a single-writer demonstration, not a production moderation service.",
    "distinctive_contribution": "The contribution is the complete evidence workflow: editable extraction, image reuse signals, contact masking before the external visual model, structured Meta observations, independent ML and a separate moderator transition. The reviewer can inspect the same processed images used for Meta analysis. The profile model deliberately excludes avatar presence, and the interface discloses the pair model's synthetic training data. These are implemented behaviors rather than promised features.",
    "privacy_and_safety": "A local OCR and Presidio pipeline identifies contact lines and covers them with padded opaque masks before provider image submission. Failed processing blocks the request. The demo verifies equality between preview, provider-prepared and reviewer-stored JPEG bytes, with no EXIF metadata in those processed images. Detection is imperfect: this is protection for detected identifiers, not a promise of complete anonymization. Reviewer evidence requires authentication. No screenshot or model score proves account ownership; the separate moderator action is demonstrated only on fictional accounts.",
    "challenges_and_tradeoffs": "OCR can confuse handles, display names and biography lines, so the report form requires review and correction. A historical fake/spam classifier also answers a different question from copied-profile detection; the project separates those signals and adds a text-reuse pair model. Excluding avatar presence guarantees avatar invariance, but did not improve every metric on the older spam holdout. The synthetic pair model and screenshot-based evidence still require external validation.",
    "what_works_now": "The English browser walkthrough records a complete fictional report, local inspection and contact masking, an uncached Meta Muse Spark response, local ML results, an under-review state, a moderator confirmation and a profile warning that persists after reload. Two example contact regions were masked; a second local OCR/Presidio scan found zero remaining detected identifier regions in those processed demo images. The most recent recorded full test run passed 123 backend and 24 frontend tests. These are development checks, not real-world accuracy measurements.",
    "what_is_next": "First, build a consented, independently labelled evaluation set that includes legitimate look-alikes, fan and parody accounts, sparse profiles, changed usernames, image crops and OCR failures. Measure false positives and recall separately for copy detection and spam patterns. Then add verified ownership evidence, appeals, audit logs, database-backed concurrency, abuse controls, monitoring and a clearly defined deployment model. Any real Instagram integration would require a separate authorized integration path.",
    "open_source_components": "PaddleOCR extracts text; imagededup compares image regions; Microsoft Presidio detects contact information for local masking; scikit-learn is used for training logistic-regression models; React, Vite and FastAPI power the web application. Embla Carousel and emoji-picker-react support the social interface. This source release includes two JSON inference artifacts and setup instructions. MIT covers original project code, with separate third-party and media notices. Raw historical training CSVs are not redistributed; the mirrored dataset's provenance and transformations still require review before other redistribution.",
    "builder_bio": "Nurzhan Zhumabekov is a Software Engineering student at Astana IT University in Astana, Kazakhstan, building web applications and AI-assisted tools. His public GitHub profile is https://github.com/Nurzhan-Zhumabekov. Confirm the complete team roster and each person's contribution before submitting any team or authorship fields.",
}

# Existing captures: exact observed UI labels are used in the directions below.
SCENES = [
    {
        "start": 0, "end": 12, "title": "The problem",
        "shots": ["01-original-profile.png", "02-copy-before-report.png"],
        "action": "Open on a simple title card: MirrorCheck / AI-Assisted Impersonation Review. Cut to the original and the suspected copy side by side. Keep the usernames legible.",
        "overlay": "Unofficial Instagram-style prototype · Fictional accounts",
        "voiceover": "An impersonator can copy a creator's photos and biography while changing just the username. MirrorCheck helps turn that suspicion into evidence a reviewer can inspect.",
    },
    {
        "start": 12, "end": 28, "title": "Show the working product",
        "shots": ["01-original-profile.png", "02-copy-before-report.png"],
        "action": "Identify aigerim.k and aigerim.k.archive. Point to the shared display name, bio, avatar graphic and gallery. Show that the copy initially has no warning.",
        "overlay": "Recorded real browser run · No real accounts reported",
        "voiceover": "This is our working, unofficial Instagram-style web prototype. These two fictional accounts share a name, biography, avatar and post images, but have different usernames.",
    },
    {
        "start": 28, "end": 50, "title": "Report and review OCR",
        "shots": ["03-report-reason.png", "04-ocr-processing.png", "06-reviewed-ml-fields.png"],
        "action": "Show Report account → Pretending to be someone else. Then show the screenshot-upload and OCR captures. Zoom the reviewed fields and I have reviewed the extracted data. Explain the corrections without pretending extraction was perfect.",
        "overlay": "PaddleOCR → editable fields → reporter review",
        "voiceover": "From the suspected copy, I choose Report account, then Pretending to be someone else. I attach screenshots of the original and suspected profile. PaddleOCR fills editable fields, and I correct the extracted text against the screenshots before submitting.",
    },
    {
        "start": 50, "end": 72, "title": "Privacy before the provider",
        "shots": ["05-ocr-redaction-preview.png"],
        "action": "Hold on the suspect preview with the email and phone lines masked. Show a small editor-added flow: local OCR + Presidio → processed JPEG → Meta AI. Add an editor-added verification note, clearly separate from the application UI: 2 regions masked; preview/provider-prepared/stored bytes match.",
        "overlay": "Detected contact lines masked locally before Meta AI",
        "voiceover": "Before any image reaches Meta AI, Presidio identifies the example email and phone. The server permanently covers both contact lines. These previews are the actual processed images prepared for Meta, with matching hashes for the evidence saved for review.",
    },
    {
        "start": 72, "end": 96, "title": "Real Meta Muse Spark analysis",
        "shots": ["07-meta-processing.png", "08-report-receipt.png", "09-meta-and-ml-results.png", "11-moderator-evidence.png"],
        "action": "Show processing, then the receipt and Meta AI summary in 09-meta-and-ml-results.png. Zoom the actual English reuse observations and ownership limitation. The supplied capture does not expose the model-version field: put muse-spark-1.3 and needs_review in a clearly editor-added caption, sourced from VERIFIED_DEMO_FACTS.json. The moderator capture shows the processed evidence images. Do not show a reviewer access code.",
        "overlay": "Real uncached Meta response · needs_review · Waiting time condensed",
        "voiceover": "Meta Muse Spark analyzes the processed screenshots through our backend and returns structured similarities, differences and limitations. Here it identifies reused profile content and recommends further review. It explicitly says screenshots cannot establish ownership. This is a real API response from the recorded run.",
    },
    {
        "start": 96, "end": 116, "title": "Independent ML and image evidence",
        "shots": ["09-meta-and-ml-results.png", "11-moderator-evidence.png"],
        "action": "Show Content reuse signals · ML, Image and name similarity and Spam patterns · ML separately. Application cards round to 72%, 86% and 94%. If adding an editor overlay with more precision, use 72.19%, 85.85% and 94.46%. Describe the imagededup result as ONE matching grid region, not six individual photo detections.",
        "overlay": "Text reuse ≠ spam patterns ≠ identity verification",
        "voiceover": "Local models add separate signals: a text-reuse comparison between the two profiles, and an auxiliary profile spam-pattern score. Image deduplication also finds a matching grid region. These scores are evidence signals, not accuracy claims or proof of identity.",
    },
    {
        "start": 116, "end": 134, "title": "Keep uncertainty visible",
        "shots": ["10-profile-under-review.png", "09-meta-and-ml-results.png"],
        "action": "Show Account under review, then the synthetic-training disclosure in the analysis. Add a small editor note: profile model excludes avatar presence. Do not suggest the demo proves every ordinary profile is safe or that an actual avatar was changed during this run.",
        "overlay": "Under review · Synthetic pair training disclosed",
        "voiceover": "The report remains Under review. Our profile model excludes avatar presence, so changing only a default-avatar flag cannot change its score. The pair model uses synthetic training data, a limitation shown to the reviewer.",
    },
    {
        "start": 134, "end": 152, "title": "Separate moderator decision",
        "shots": ["11-moderator-evidence.png", "12-moderator-decision.png", "13-decision-saved.png"],
        "action": "Show the relevant claim's processed evidence, then the Decision saved capture. The supplied 12-moderator-decision.png is cropped to evidence; the action button and click are outside the capture. Describe Confirm impersonation through narration and an editor-added caption, not a fabricated button or click. This is a replay of the authorized fictional demo, where the operator also played the moderator; it is not an independent identity investigation.",
        "overlay": "Moderator action required · Fictional demonstration",
        "voiceover": "In the moderator view, I inspect the processed images and analysis, then explicitly select Confirm impersonation for this fictional case. The AI recommendation alone cannot perform this transition.",
    },
    {
        "start": 152, "end": 170, "title": "Warning and persistence",
        "shots": ["14-profile-labelled.png", "15-label-after-reload.png"],
        "action": "Hold on Impersonation confirmed. Cut to the after-reload capture. If recording the live labelled page now, reload it and show the saved warning; do not reset the existing report to recreate the earlier state.",
        "overlay": "Impersonation confirmed · Persists after reload",
        "voiceover": "The profile now displays Impersonation confirmed. Reloading preserves the warning because the decision is stored on the server. This demonstrates the complete report-to-review workflow; it does not modify the real Instagram service.",
    },
    {
        "start": 170, "end": 180, "title": "Close with the value and next step",
        "shots": ["15-label-after-reload.png"],
        "action": "End on MirrorCheck, the one-line value proposition and Meta Muse Spark + local evidence + moderator review. Add the repository URL only after it contains the current source and license. End at 03:00 or earlier.",
        "overlay": "Review suspected copies. Reduce contact exposure. Keep a moderator in control.",
        "voiceover": "MirrorCheck makes suspicious copies easier to review while reducing contact exposure. Next, we need consented real-world evaluation and production hardening.",
    },
]


def words(value: str) -> int:
    return len(re.findall(r"\S+", value))


def clock(seconds: int) -> str:
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def srt_clock(seconds: float) -> str:
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write(name: str, value: str) -> None:
    (KIT / name).write_text(value.strip() + "\n", encoding="utf-8")


def make_captions() -> tuple[str, list[dict]]:
    """Evenly time short caption chunks within each planned scene; not audio alignment."""
    cues = []
    for scene in SCENES:
        # Balance words across cues to avoid a one-word, sub-second final cue.
        tokens = scene["voiceover"].split()
        minimum = max(math.ceil(len(scene["voiceover"]) / 75), math.ceil((scene["end"] - scene["start"]) / 7))
        for count in range(minimum, len(tokens) + 1):
            chunks = []
            for i in range(count):
                chunk = " ".join(tokens[round(len(tokens) * i / count):round(len(tokens) * (i + 1) / count)])
                lines = textwrap.wrap(chunk, width=42, break_long_words=False, break_on_hyphens=False)
                chunks.append("\n".join(lines))
            if not all(1 <= len(chunk.splitlines()) <= 2 for chunk in chunks):
                continue
            sizes = [len(chunk.replace("\n", " ")) for chunk in chunks]
            total = sum(sizes)
            consumed = 0
            candidate = []
            for chunk, size in zip(chunks, sizes):
                start = scene["start"] + (scene["end"] - scene["start"]) * consumed / total
                consumed += size
                end = scene["start"] + (scene["end"] - scene["start"]) * consumed / total
                candidate.append({"start": start, "end": end, "text": chunk})
            if all(2 <= cue["end"] - cue["start"] <= 7 for cue in candidate):
                cues.extend(candidate)
                break
        else:
            raise ValueError(f"Could not fit readable captions to scene {scene['title']}")
    srt = "\n\n".join(
        f"{i}\n{srt_clock(cue['start'])} --> {srt_clock(cue['end'])}\n{cue['text']}"
        for i, cue in enumerate(cues, 1)
    )
    return srt + "\n", cues


def main() -> None:
    KIT.mkdir(exist_ok=True)
    (KIT / "stills").mkdir(exist_ok=True)
    publication_path = KIT / "REPOSITORY_PUBLICATION.json"
    publication = json.loads(publication_path.read_text(encoding="utf-8")) if publication_path.exists() else None
    video_path = KIT / "VIDEO_VERIFICATION_EN.json"
    video = json.loads(video_path.read_text(encoding="utf-8")) if video_path.exists() else None
    if video:
        assert (ROOT / video["file"]).is_file() and video["duration_seconds"] == 180
    verification_path = DEMO / "verification.json"
    if not verification_path.exists():
        verification_path = KIT / "DEMO_VERIFICATION.json"
    evidence = json.loads(verification_path.read_text(encoding="utf-8"))
    historical_tests = ROOT / "outputs/english-ui/verification.json"
    if historical_tests.exists():
        tests = json.loads(historical_tests.read_text(encoding="utf-8"))
    else:
        previous_facts = json.loads((KIT / "VERIFIED_DEMO_FACTS.json").read_text(encoding="utf-8"))
        tests = {"backend_tests": previous_facts["recorded_full_suite"]["backend"],
                 "frontend_tests": previous_facts["recorded_full_suite"]["frontend"]}
    write("DEMO_VERIFICATION.json", json.dumps(evidence, indent=2, ensure_ascii=True))
    assert evidence["claim_id"] == "5828394c"
    assert evidence["meta"]["model"] == "muse-spark-1.3" and evidence["meta"]["cached"] is False
    assert evidence["status"] == "confirmed" and evidence["preview_equals_stored_provider_bytes"]
    assert evidence["redaction"]["regions_masked"] == 2 and evidence["matched_regions"] == 1
    assert tests["backend_tests"] == 123 and tests["frontend_tests"] == 24
    assert SCENES[0]["start"] == 0 and SCENES[-1]["end"] == 180
    for previous, current in zip(SCENES, SCENES[1:]):
        assert previous["end"] == current["start"]

    for shot in sorted({name for scene in SCENES for name in scene["shots"]}):
        source = DEMO / shot if (DEMO / shot).exists() else KIT / "stills" / shot
        raw = source.read_bytes()
        assert hashlib.sha256(raw).hexdigest() == evidence["screenshots_sha256"][shot]
        target = KIT / "stills" / shot
        if source.resolve() != target.resolve():
            shutil.copy2(source, target)

    # Preserve existing notices alongside the captured interface; no relicensing.
    shutil.copy2(ROOT / "web/public/photo-credits.html", KIT / "EXISTING_PHOTO_CREDITS.html")
    shutil.copy2(ROOT / "web/public/open-source-licenses.txt", KIT / "EXISTING_COMPONENT_NOTICES.txt")

    write("PROJECT_DESCRIPTION_EN.md", f"""# {TITLE} — {SUBTITLE}

Working submission title. This packet does not rename the application or claim an official affiliation.

## One-line pitch ({len(TAGLINE)} characters)

{TAGLINE}

## Main project description ({words(DESCRIPTION)} words)

{DESCRIPTION}

## Short description ({words(SHORT_DESCRIPTION)} words)

{SHORT_DESCRIPTION}

## Compact description ({words(VERY_SHORT)} words)

{VERY_SHORT}

## Recommended positioning

- Track recommendation: Indie developer, if this matches the actual registration and team eligibility.
- Theme recommendation: Build for Your World.
- Category: AI-assisted trust and safety / social-platform feature prototype.
- Submission status: working local prototype; this packet is a draft for the owner to review and submit.

The final authenticated form's field labels and character limits were not accessible in this session. Choose the variant that fits the actual field; the word counts above are measured, not organizer limits.
""")

    sections = [f"# {TITLE} — adaptable submission answers\n\nPrepared in English on November 4, 2026. These are content blocks, not a verified transcription of the final form. No form has been filled or submitted.\n\nProject name: **{TITLE} — {SUBTITLE}**\n\nTagline: {TAGLINE}\n\nMain and shorter descriptions: [PROJECT_DESCRIPTION_EN.md](PROJECT_DESCRIPTION_EN.md)."]
    labels = {
        "problem_and_users": "Problem and intended users",
        "solution_and_workflow": "What the project does",
        "meta_model_usage": "How Meta AI is used",
        "why_meta_matters": "Why Meta AI is central to the project",
        "technical_implementation": "How it is built",
        "distinctive_contribution": "What is distinctive",
        "privacy_and_safety": "Privacy, safety and decision boundaries",
        "challenges_and_tradeoffs": "Challenges and tradeoffs",
        "what_works_now": "Current accomplishments and validation",
        "what_is_next": "Next steps",
        "open_source_components": "Open-source components and attribution",
        "builder_bio": "Builder bio / team field draft",
    }
    for key, value in ANSWERS.items():
        sections.append(f"## {labels[key]} ({words(value)} words)\n\n{value}")
    sections.append(f"""## Links and owner-only fields

| Item | Verified status / required action |
| --- | --- |
| GitHub | {REPO} — this source release includes the web application, legacy client, tests, JSON models and an MIT license for original code. Check `REPOSITORY_PUBLICATION.json` when present for the application commit verified after upload. |
| Demo video URL | Not yet available. Record/export/upload the three-minute video, then test the viewing link while signed out. |
| Public application URL | Not verified or prepared here. `localhost:8090` is accessible only on the development machine. Do not paste it as a public demo URL. |
| Track | Indie developer is recommended for a student/individual entry; confirm the actual registration. |
| Theme | Build for Your World is recommended. |
| Team members / contributions | Owner to verify. Do not invent additional contributors or claim sole authorship without checking. |
| Eligibility / agreements | Owner to read the actual terms and answer personally. This packet makes no eligibility attestations. |
| Submission destination | [Cerebral Valley submission form]({FORM}). Authentication is needed to verify the final questions and limits. |
""")
    write("SUBMISSION_ANSWERS_EN.md", "\n\n".join(sections))

    narration = "\n\n".join(scene["voiceover"] for scene in SCENES)
    script = [f"""# {TITLE} — three-minute demo-video script

Target runtime: **03:00 maximum for this edit plan**, matching the organizer's three-minute demo guidance. The exact form's upload restrictions were not visible; check them before upload.

Voiceover: **{words(narration)} words**, approximately {words(narration) / 3:.0f} words per minute across the full video. Individual scenes leave room for visual pauses. Read in a calm, conversational voice; no need to read handles, percentages or implementation versions aloud.

Format: 1920 × 1080 landscape is an editing recommendation, not a verified organizer requirement. Use 1080p legible crops, a clean English interface, and an audible English voiceover.

This script uses the **real recorded run** of fictional claim `5828394c`, verified November 4, 2026. Captures are supplied in [stills/](stills/). They are already-recorded evidence, not a new live Meta request. Keep the lower-third **Recorded real browser run · Fictional accounts** visible during the replay; label condensed processing time. This packet contains no finished video or recorded audio.

The current demo claim is already confirmed. Use its earlier real captures for the before/under-review stages; do not reset stored reports to stage a new transition. The operator played both reporter and moderator in this fictional demonstration.
"""]
    for index, scene in enumerate(SCENES, 1):
        shotlinks = ", ".join(f"[{name}](stills/{name})" for name in scene["shots"])
        script.append(f"""## {clock(scene['start'])}–{clock(scene['end'])} · {index}. {scene['title']}

**Screen / edit:** {scene['action']}

**Source captures:** {shotlinks}

**On-screen text:** {scene['overlay']}

**Say:**

> {scene['voiceover']}
""")
    script.append("""## Notes for the edit

- Preserve the English labels: `Report account`, `Pretending to be someone else`, `I have reviewed the extracted data`, `Under review`, `Confirm impersonation`, `Impersonation confirmed`.
- Put editor-added titles, diagrams and precision metrics on a clearly separate overlay; do not paint new controls or observations into the application capture.
- The actual application rounds the result cards. Exact evidence values are combined similarity 85.85%, pair text reuse 72.19%, profile spam patterns 94.46%. These are three different signals, not three accuracy measurements.
- imagededup matched one grid region in this run. Meta observed reuse across the first six gallery images. Those statements are different and must not be combined into a claim of six separate imagededup matches.
- The redaction scan found zero remaining *detected* identifier regions in these processed demo images. Do not say that every identifier is always removed or that all user data stay local: the processed screenshots go to Meta.
- Do not record server consoles, `.env`, access codes, unrelated claims, email tabs, API dashboards or billing screens.
- The existing moderator stills show evidence and the saved-decision receipt, not the actual button click. Narrate that transition over an editor caption. If continuous click footage is required, it must be recorded separately with another explicitly fictional case; do not reset this completed report or invent click footage.
- `CAPTIONS_EN.srt` is timed to this plan, not to a recording. Retiming against the finished narration is required before export.
- Existing image and component attributions are copied into [EXISTING_PHOTO_CREDITS.html](EXISTING_PHOTO_CREDITS.html) and [EXISTING_COMPONENT_NOTICES.txt](EXISTING_COMPONENT_NOTICES.txt), without relicensing. The existing photo-credits page concerns the football media expansion; it is not an exhaustive provenance audit of every earlier stock image visible in the prototype. Keep applicable notices and verify the media used in the final export before public distribution.
""")
    write("DEMO_VIDEO_SCRIPT_EN.md", "\n\n".join(script))
    write("VOICEOVER_EN.txt", narration)
    srt, cues = make_captions()
    write("CAPTIONS_EN.srt", srt)

    write("RECORDING_AND_SUBMISSION_CHECKLIST_EN.md", f"""# Recording and submission checklist

## Current state

Prepared: English description variants, adaptable answer blocks, a 180-second edit plan, exact voiceover text, draft SRT captions, and 15 real browser stills from the fictional English run.

This packet is distributed with the application source, bundled JSON models, setup instructions and an MIT license for original code. No finished narrated video, video hosting, public application deployment or final hackathon submission is included. `REPOSITORY_PUBLICATION.json`, when present, records verified source publication separately.

## Deadline and source of the requirements

- Published project deadline: **November 4, 2026 at 9:00 PM US Eastern (EST, UTC−5)**.
- Same instant: **November 5, 2026 at 02:00 UTC / 07:00 in Astana (UTC+5)**.
- [Official Meta event page]({OFFICIAL}) and [Cerebral Valley event page](https://cerebralvalley.ai/e/meta-ai-developer-hackathon) publish the deadline. Dates may change; check the live form before final submission.
- Organizer email dated November 3, 2026 UTC calls for a **three-minute demo video** and says an **open-source GitHub repository is mandatory**. This packet does not reproduce private email headers or contact details.
- The authenticated [submission form]({FORM}) was not readable in this session. No exact field limits, video-host restrictions or other unseen requirements are asserted.

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

Repository: {REPO}. This release supplies the implementation and MIT license for original code. See `REPOSITORY_PUBLICATION.json`, when present, for a verified uploaded application commit. Keep these checks when preparing a later update.

- [ ] Publish the current native web frontend, backend, local workers, tests, scripts, dependency manifests and setup documentation.
- [ ] Add an appropriate license for code the owner has the right to license; preserve third-party notices and media credits. Public visibility alone does not provide an open-source license.
- [ ] Exclude `.env`, worker/reviewer keys, logs, raw reports, private evidence, caches, virtual environments and `node_modules`. Do not upload the entire `outputs/` directory.
- [ ] ML artifacts live under ignored `outputs/ml/`. Ensure a clean checkout either contains reviewed non-secret inference artifacts in a documented distribution path, or can reproduce them using the training scripts. Do not promise clone-and-run inference while artifacts are missing.
- [ ] The screenshot workers require additional environments/models. Document their setup and initial downloads, not only the web launcher. A server Meta API key is required for live external analysis.
- [ ] Review the provenance and redistribution terms of the historical profile dataset and derived assets. Do not automatically bundle mirrored raw CSVs. Keep ML limitations visible.
- [ ] Include a small explicitly fictional sample case and a safe walkthrough. Do not include real complaint records or organizer mail.
- [ ] Test the exact public commit from a clean checkout. Confirm installation, web build, worker readiness and whether inference artifacts are present. Existing local tests are not proof of a reproducible public release.
- [ ] Open the repository while signed out. Verify code, license, README, setup and demo/video links are accessible.

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
""")

    write("FACTS_AND_SOURCES_EN.md", f"""# Facts and sources for the submission

Prepared November 4, 2026. Project evidence below comes from already-recorded verification files, not a new full test run or a fresh Meta request during document preparation.

## Verified fictional run

Source: `outputs/browser-english-flow-20261104/verification.json`, verified at `{evidence['verified_at']}`. A minimal copy of the relevant facts is provided in [VERIFIED_DEMO_FACTS.json](VERIFIED_DEMO_FACTS.json).

| Claim | Supported wording | Limit |
| --- | --- | --- |
| Real Meta use | Meta Model API, `muse-spark-1.3`, uncached response, recommendation `needs_review` | Not a new call made for this packet; no fine-tuning claim |
| Demo accounts | Fictional `aigerim.k` and `aigerim.k.archive` | Not real Instagram accounts or a real identity investigation |
| Combined similarity | {evidence['combined_similarity']:.2%} | A comparison signal for one input, not measured accuracy |
| Pair text-reuse ML | {evidence['pair_ml']:.2%} | Synthetic pair training; real-world performance unvalidated |
| Auxiliary profile ML | {evidence['profile_ml']:.2%} | Historical fake/spam patterns; not an impersonation probability |
| Image deduplication | {evidence['matched_regions']} matching grid region | Not six independently matched photo regions in this run |
| Redaction | {evidence['redaction']['regions_masked']} detected contact regions masked | Detected identifiers only; no blanket anonymity guarantee |
| Second local scan | 0 remaining detected identifier regions in the processed demo images | Detector-dependent, not proof that every possible identifier is absent |
| Evidence consistency | Preview, provider-prepared and stored JPEG bytes match | Processing integrity, not identity authenticity |
| Unauthenticated evidence request | HTTP {evidence['unauthenticated_evidence_status']} | Limited demonstrated check, not a complete security audit |
| Decision and persistence | `under_review` → separate moderator action → `confirmed`, warning survives reload | Operator played both roles in the fictional demonstration |
| OCR | Editable fields reviewed and corrected against screenshots | Do not claim perfect automatic extraction |

The application rounds the three result cards to 86%, 72% and 94%. Exact evidence values above are available for a clearly labelled editor overlay, if needed.

## Tests and ML context

- Latest recorded full suite: **{tests['backend_tests']} backend + {tests['frontend_tests']} frontend = {tests['backend_tests'] + tests['frontend_tests']} passing tests**, recorded in `outputs/english-ui/verification.json`. The subsequent English browser-run record includes a successful web build, English-copy test and formatting check. No full suite was rerun merely to write these documents.
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

- [Meta official hackathon page]({OFFICIAL}): deadline November 4 at 9 PM ET, tracks and themes. Checked during preparation. For November 4, 2026, US Eastern is UTC−5; Astana is UTC+5, giving November 5 at 07:00 Astana.
- [Cerebral Valley event page](https://cerebralvalley.ai/e/meta-ai-developer-hackathon): event context and key dates. Application-selection guidance must not be represented as an unseen final-project rubric.
- Organizer reminder dated November 3, 2026 UTC: three-minute demo guidance; mandatory open-source GitHub repository. Private message contents and headers are not bundled.
- [Submission form]({FORM}): sign-in was required to inspect the actual final fields. Exact limits and upload rules are unverified here.
- [Project GitHub repository]({REPO}): initially public and empty when the packet was first prepared. The source release adds implementation and license; `REPOSITORY_PUBLICATION.json`, when present, records the actual application commit and checks verified after upload.

## Language to avoid

Avoid: “official Instagram feature”, “100% detection”, “proves who owns the account”, “fully anonymous”, “all data stay local”, “94% accurate”, “six imagededup photo matches” for this run, “independent moderator verified a real account”, “live demo” for a still-image replay, “production ready”, “published open-source implementation” while the repository is empty.

Use the concrete implemented behavior and its scope instead. Video upload and final hackathon submission remain unfinished. Source publication is a separate verified action when documented in `REPOSITORY_PUBLICATION.json`.
""")

    facts = {
        "source_verified_at": evidence["verified_at"],
        "claim_id": evidence["claim_id"],
        "fictional_accounts": ["aigerim.k", "aigerim.k.archive"],
        "meta": evidence["meta"],
        "combined_similarity": evidence["combined_similarity"],
        "pair_text_reuse_ml": evidence["pair_ml"],
        "profile_spam_patterns_ml": evidence["profile_ml"],
        "matched_image_regions": evidence["matched_regions"],
        "masked_contact_regions": evidence["redaction"]["regions_masked"],
        "preview_equals_stored_provider_bytes": evidence["preview_equals_stored_provider_bytes"],
        "local_redaction_rescan": evidence["local_redaction_rescan"],
        "public_status_after_reload": evidence["public_status_after_reload"],
        "operator_played_moderator": True,
        "real_world_copy_accuracy_established": False,
        "scores_prove_ownership": False,
        "recorded_full_suite": {"backend": tests["backend_tests"], "frontend": tests["frontend_tests"]},
    }
    write("VERIFIED_DEMO_FACTS.json", json.dumps(facts, indent=2, ensure_ascii=True))

    fields = {
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "status": "local_draft_not_submitted",
        "title": TITLE,
        "subtitle": SUBTITLE,
        "tagline": TAGLINE,
        "description": DESCRIPTION,
        "short_description": SHORT_DESCRIPTION,
        "compact_description": VERY_SHORT,
        "recommended_track": "Indie developer (confirm registration and eligibility)",
        "recommended_theme": "Build for Your World",
        "actual_form_fields_and_limits_verified": False,
        "repository_url": REPO,
        "repository_status": "published_and_verified" if publication else "source_release_prepared_for_upload",
        "repository_publication": publication,
        "video_url": video["video_url"] if video else None,
        "video_verification": video,
        "public_demo_url": None,
        "team_roster_confirmed": False,
        "deadline_et": "2026-11-04T21:00:00-05:00",
        "deadline_astana": "2026-11-05T07:00:00+05:00",
        "answers": ANSWERS,
        "scenes": SCENES,
        "word_counts": {"main": words(DESCRIPTION), "short": words(SHORT_DESCRIPTION), "compact": words(VERY_SHORT), "voiceover": words(narration)},
        "character_counts": {"title": len(TITLE), "tagline": len(TAGLINE), "main": len(DESCRIPTION), "short": len(SHORT_DESCRIPTION), "compact": len(VERY_SHORT)},
    }
    write("SUBMISSION_FIELDS.json", json.dumps(fields, indent=2, ensure_ascii=True))

    write("README_FIRST.md", f"""# {TITLE} — English submission packet

Prepared for the Meta Global AI Developer Hackathon on November 4, 2026. Working title: **{TITLE} — {SUBTITLE}**. The current application is still the unofficial Instagram feature concept; no rebranding or official affiliation is implied.

## Use these files

| File | Purpose |
| --- | --- |
| [PROJECT_DESCRIPTION_EN.md](PROJECT_DESCRIPTION_EN.md) | Main English description, short alternatives and one-line pitch |
| [SUBMISSION_ANSWERS_EN.md](SUBMISSION_ANSWERS_EN.md) | Adaptable answers for implementation, Meta usage, challenges and next steps |
| [DEMO_VIDEO_SCRIPT_EN.md](DEMO_VIDEO_SCRIPT_EN.md) | Exact 00:00–03:00 scene plan, screen directions and spoken English |
| [VOICEOVER_EN.txt](VOICEOVER_EN.txt) | Narration only, ready for a teleprompter |
| [CAPTIONS_EN.srt](CAPTIONS_EN.srt) | Draft timed captions; align with the actual recording before export |
| [stills/](stills/) | 15 authentic captures from the completed fictional browser run |
| [RECORDING_AND_SUBMISSION_CHECKLIST_EN.md](RECORDING_AND_SUBMISSION_CHECKLIST_EN.md) | Recording, repository and final-submission actions |
| [FACTS_AND_SOURCES_EN.md](FACTS_AND_SOURCES_EN.md) | Evidence, sources, model limitations and careful claim wording |
| [VERIFIED_DEMO_FACTS.json](VERIFIED_DEMO_FACTS.json) | Minimal non-secret facts from the existing real Meta run |
| [DEMO_VERIFICATION.json](DEMO_VERIFICATION.json) | Recorded demo verification and screenshot hashes for rebuilding this packet |
| [SUBMISSION_FIELDS.json](SUBMISSION_FIELDS.json) | Copy blocks, counts, planned scenes and explicit missing links |
| [EXISTING_PHOTO_CREDITS.html](EXISTING_PHOTO_CREDITS.html) / [EXISTING_COMPONENT_NOTICES.txt](EXISTING_COMPONENT_NOTICES.txt) | Existing project attribution notices, preserved without relicensing |
| [PACKET_VALIDATION.json](PACKET_VALIDATION.json) | Document/asset checks from packet generation; not an app test run |

## What remains before the owner submits

1. Verify the source at {REPO}, including bundled models and the original-code MIT license. `REPOSITORY_PUBLICATION.json`, when present, records the verified application commit.
2. Record, edit and upload the three-minute video; its viewing URL is not available yet.
3. Open the authenticated [submission form]({FORM}), confirm actual limits, team/track details and agreements, and submit with the real links. No final form was filled or submitted here.

Deadline currently published by the organizers: **November 4, 2026, 9 PM ET = November 5, 2026, 07:00 Astana**. See the checklist for sources and the distinction between organizer guidance and editing recommendations.

The supplied stills and local [English walkthrough](http://localhost:8090/english-report-walkthrough.html) replay an actual completed fictional run. They are not a finished video, a new live inference, or a public application deployment. Any third-party media notices continue to apply. No real complaint records, private organizer emails, server credentials or model API keys are included.

The source checkout can rebuild this packet with `python scripts/build_submission_kit.py`, using the bundled verification snapshot and stills when private development outputs are absent. The distribution archive is also in `releases/submission-kit-20261104.zip`.
""")

    if publication:
        readme = KIT / "README_FIRST.md"
        with readme.open("a", encoding="utf-8") as output:
            output.write("\nVerified source publication: [REPOSITORY_PUBLICATION.json](REPOSITORY_PUBLICATION.json).\n")
        checklist = KIT / "RECORDING_AND_SUBMISSION_CHECKLIST_EN.md"
        completed_prefixes = (
            "Publish the current native web frontend", "Add an appropriate license",
            "Exclude `.env`", "The screenshot workers require", "Include a small explicitly fictional sample case",
            "Test the exact public commit", "Open the repository while signed out",
        )
        content = checklist.read_text(encoding="utf-8")
        for prefix in completed_prefixes:
            content = content.replace("- [ ] " + prefix, "- [x] " + prefix)
        content = content.replace(
            "- [ ] ML artifacts live under ignored `outputs/ml/`. Ensure a clean checkout either contains reviewed non-secret inference artifacts in a documented distribution path, or can reproduce them using the training scripts. Do not promise clone-and-run inference while artifacts are missing.",
            "- [x] Both JSON inference models are bundled in `models/`; the installer and clean-clone inference were verified. Runtime copies stay under ignored `outputs/ml/`.")
        checklist.write_text(content, encoding="utf-8")

    if video:
        url = video["video_url"]
        for filename in ["README_FIRST.md", "SUBMISSION_ANSWERS_EN.md", "RECORDING_AND_SUBMISSION_CHECKLIST_EN.md", "FACTS_AND_SOURCES_EN.md"]:
            path = KIT / filename
            content = path.read_text(encoding="utf-8")
            content = content.replace(
                "Not yet available. Record/export/upload the three-minute video, then test the viewing link while signed out.",
                f"[Finished 03:00 English MP4]({url}). Check the actual form's accepted video hosts before using a repository MP4 URL.")
            content = content.replace(
                "No finished narrated video, video hosting, public application deployment or final hackathon submission is included.",
                "The finished narrated video is distributed as a source-release MP4. Public application deployment and final hackathon submission are not included. Check the form's video-host requirements.")
            content = content.replace(
                "2. Record, edit and upload the three-minute video; its viewing URL is not available yet.",
                "2. The three-minute video is recorded and included in the source release. Check the actual form's host restrictions and upload to an accepted host if required.")
            content = content.replace(
                "Video upload and final hackathon submission remain unfinished.",
                "The completed video is distributed as a source-release MP4; acceptance of that host in the final form remains unverified. Final hackathon submission is unfinished.")
            content += "\nFinished video and its newer fictional case: [VIDEO_DELIVERY_EN.md](VIDEO_DELIVERY_EN.md). The original script and stills describe the earlier archive-profile run.\n"
            path.write_text(content, encoding="utf-8")

    # Focused document validation. No application or provider state is changed.
    assert words(DESCRIPTION) <= 350
    assert words(SHORT_DESCRIPTION) <= 110 and words(VERY_SHORT) <= 60
    assert len(TAGLINE) <= 160
    assert 300 <= words(narration) <= 400
    assert all(words(scene["voiceover"]) / (scene["end"] - scene["start"]) * 60 <= 150 for scene in SCENES)
    assert all(cue["end"] > cue["start"] and len(cue["text"].splitlines()) <= 2 for cue in cues)
    assert all(len(line) <= 42 for cue in cues for line in cue["text"].splitlines())
    assert all(2 <= cue["end"] - cue["start"] <= 7.01 for cue in cues)
    assert all(len(cue["text"].replace("\n", " ")) / (cue["end"] - cue["start"]) <= 17 for cue in cues)
    assert cues[0]["start"] == 0 and cues[-1]["end"] == 180
    assert all(cues[i]["end"] <= cues[i + 1]["start"] + 1e-9 for i in range(len(cues) - 1))
    assert all(not re.search("[\u0400-\u04ff]", p.read_text(encoding="utf-8")) for p in KIT.iterdir() if p.suffix in {".md", ".txt", ".srt", ".json"})

    secrets = [str(v) for k, v in dotenv_values(ROOT / ".env").items() if v and any(term in k for term in ("KEY", "TOKEN", "PASSWORD", "SECRET"))]
    worker_key = ROOT / "outputs/evidence-worker.key"
    if worker_key.exists():
        secrets.append(worker_key.read_text(encoding="utf-8").strip())
    for path in KIT.rglob("*"):
        if path.is_file():
            assert path.suffix in {".md", ".txt", ".srt", ".json", ".png", ".html"}
            data = path.read_bytes()
            for secret in secrets:
                assert not secret or secret.encode() not in data, f"Secret detected in {path.name}"
    # All relative Markdown targets must resolve. URLs and anchor-only links are excluded.
    for path in KIT.glob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" not in target and not target.startswith("#"):
                if target == "PACKET_VALIDATION.json":
                    continue
                assert (path.parent / target.split("#")[0]).exists(), (path.name, target)

    validation = {
        "validated_at": datetime.now(timezone.utc).isoformat(),
        "description_word_counts": fields["word_counts"],
        "tagline_characters": len(TAGLINE),
        "timeline_seconds": 180,
        "scene_count": len(SCENES),
        "max_scene_voiceover_words_per_minute": round(max(words(s["voiceover"]) / (s["end"] - s["start"]) * 60 for s in SCENES), 1),
        "draft_caption_cues": len(cues),
        "captions_max_lines": 2,
        "captions_max_line_characters": 42,
        "captions_min_seconds": round(min(cue["end"] - cue["start"] for cue in cues), 2),
        "captions_max_seconds": round(max(cue["end"] - cue["start"] for cue in cues), 2),
        "captions_need_alignment_to_recorded_audio": True,
        "source_stills_verified_against_recorded_sha256": 15,
        "english_text_only": True,
        "relative_links_resolve": True,
        "known_server_secrets_scan": "passed",
        "finished_video_exists": video is not None,
        "submitted": False,
        "source_repository_published": publication is not None,
        "app_tests_rerun_for_document_preparation": False,
    }
    write("PACKET_VALIDATION.json", json.dumps(validation, indent=2, ensure_ascii=True))

    files = sorted(path for path in KIT.rglob("*") if path.is_file())
    ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, Path("MirrorCheck-submission") / path.relative_to(KIT))
    with zipfile.ZipFile(ARCHIVE) as bundle:
        assert bundle.testzip() is None and len(bundle.infolist()) == len(files)
        assert not any(name.endswith((".env", ".key")) for name in bundle.namelist())
    release_root = ROOT / "releases"
    release_root.mkdir(exist_ok=True)
    shutil.copy2(ARCHIVE, release_root / ARCHIVE.name)
    print(json.dumps({"packet": str(KIT), "archive": str(ARCHIVE), "files": len(files), "archive_bytes": ARCHIVE.stat().st_size, "validation": validation}, indent=2))


if __name__ == "__main__":
    main()

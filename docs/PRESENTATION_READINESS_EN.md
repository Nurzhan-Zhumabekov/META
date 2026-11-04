# MirrorCheck presentation readiness

This is an internal assessment of the hackathon MVP, separate from the organizer's judging rubric, prize decisions and model accuracy.

| Area | Points | Evidence |
| --- | ---: | --- |
| Problem and usefulness | 18/20 | Account-copy review, human decisions and a dismissal path |
| Complete product scenario | 19/20 | Recorded confirmed and rejected cases, persisted statuses and profile integration |
| AI and ML integration | 16/20 | Real Meta calls; separate text/spam ML; OCR, redaction and corrected photo extraction |
| Design and usability | 14/15 | English UI; separate AI recommendation, moderator decision and score sources |
| Engineering | 14/15 | Tested routing, privacy boundary, protected reviewer workflow and strict preflight |
| Demonstration and handoff | 9/10 | Demo guide, narrated three-minute video, both outcomes and English submission materials |
| Total | 90/100 | Internal MVP assessment |

## Reproduce the checks

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv-vision\Scripts\python.exe -m pytest vision_tests -q
.\.venv-privacy\Scripts\python.exe -m pytest privacy_tests -q
cd web
npm test
npm run build
cd ..
.\scripts\run_web.ps1 -RequireMeta
```

The preflight checks dependencies and direct application routes. A status 200 alone is insufficient. A failed check stops the strict launcher. It writes no claims and makes no paid model requests.

Open [the demo guide](http://localhost:8090/demo-guide.html). Its badges read live service status; its video and walkthroughs are recorded evidence.

## Improvements after the 82-point assessment

- Reproduced the zero-match error with actual four-column captures: a darkened gutter merged two photos and Messages enlarged a crop into the side panel.
- Kept wide whitespace as a boundary and recovered integer-width merged cells only with two other agreeing widths.
- Added cases for original captures, resized/compressed JPEGs and an obscured synthetic grid. Identical-photo, unrelated-photo, avatar-only, dark/blank and compressed-gutter tests remain required.
- Kept PHash, DHash and pixel-correlation match thresholds unchanged. Shared photography does not auto-confirm a report.
- Displayed Meta's visual score separately from the 80% visual / 20% username combined score, with one decimal place. Older records without a visual score do not receive an invented value.
- Displayed Meta's recommendation and the saved human decision separately, including insufficient evidence and dismissal.
- Added a strict launcher and read-only preflight with fail-closed tests for unavailable Meta, ML and privacy services.

## Remaining limits

Independent, consented real-account evaluation is still needed. Pair ML uses synthetic pairs and profile ML targets historical spam-like patterns. Scores are not identity probabilities. Photo extraction assumes a light rectangular grid; unusual layouts, substantial crops and edits can still hide matches.

Public production use needs real reporter authentication, per-report authorization, a shared database, durable sessions and stronger abuse controls. The positive video is an edited sequence of authentic screenshots with synthesized narration. The same operator performed the fictional reporter and moderator roles.

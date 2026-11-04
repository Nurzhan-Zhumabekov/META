# Fake Account Report

An unofficial Instagram feature concept for the Meta hackathon, Indie track.
Submission deadline recorded in the project: Nov 4, 21:00 ET.
A user submits two profile screenshots, the backend analyzes visible content reuse,
and a human reviewer confirms or rejects the report.

- `src/`: FastAPI, local comparison and the Meta vision client.
- `mobile/`: Flutter interface, report form and reviewer tools.
- `app.py`: optional Gradio interface sharing the JSON database.
- `scripts/verify_meta.py`: readiness check, live smoke test and optional activation.
- `evals/`: 15 synthetic screenshot scenarios for live prompt evaluation.

## Run locally

```powershell
cd C:\Users\admin\Desktop\meta\project
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# Create .env from .env.example only if absent. Preserve ADMIN_TOKEN.
.\.venv\Scripts\python.exe -m uvicorn src.api:app --host 127.0.0.1 --port 8000
```

The web server serves `mobile/build/web` on `http://localhost:8090/`.
For a release, use the same reviewer token as the server:

```powershell
cd mobile
flutter build web --release --no-web-resources-cdn --dart-define-from-file=..\outputs\reviewer-defines.json
```

The reviewer define file is ignored by Git and is for this local demo. That shared
reviewer secret is compiled into the web build; it is not production authentication.
The **Meta API key is server-only** and is never a Dart define.

## Profile ML (works without a Meta key)

The report form can also score explicit account facts using an independently trained
9-feature logistic regression model. This estimates fake/spam-like profile patterns,
not ownership or impersonation. Its score is kept separate from screenshot similarity.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.\.venv\Scripts\python.exe scripts\train_profile_ml.py --download
```

Weights and metrics are stored as safe JSON under ignored `outputs/ml`; no upstream
notebook or pickle is executed. See [ML_INTEGRATION.md](ML_INTEGRATION.md) for the full
repository audit, provenance, measured holdout errors and limitations.

`POST /ml/profile-risk` accepts `handle`, `display_name`, `bio`, booleans
`has_profile_picture`, `has_external_url`, `is_private`, and integer counts `num_posts`,
`num_followers`, `num_following`. `/claims` optionally takes the same object as a JSON
`profile_facts` multipart field. It must describe the suspect handle. The result is
stored under `analysis.profile_ml` and never changes the human review status.

`ML_ENABLED=true` enables this optional branch when the model exists. `ML_MODEL_PATH`
overrides the default `outputs/ml/profile_risk_model.json` path. All facts are explicitly
user-provided; the prototype does not scrape Instagram or infer counts from images.

## Activate Meta AI

Live smoke verification succeeded on 2026-10-28 using `muse-spark-1.3`: two built-in
demo screenshots produced validated structured evidence (1,419 input / 533 output
tokens). The local server is configured for `COMPARER=meta`; profile ML stays enabled.
The key is stored only in the ignored server `.env`. A fresh checkout requires its
own working API key and credits.
Without a key, keep `COMPARER=local`; the UI explicitly labels local results.

1. Add `META_API_KEY=...` to the project `.env`. `MODEL_API_KEY` is also supported.
2. Check configuration without network calls:

   ```powershell
   .\.venv\Scripts\python.exe scripts\verify_meta.py
   ```

3. Test the two built-in demo screenshots and activate only after success:

   ```powershell
   .\.venv\Scripts\python.exe scripts\verify_meta.py --live --activate
   ```

4. Restart the API. Changing the Meta key/mode needs no Flutter rebuild.
   Check `GET /analysis/status` and open the report form.

The live check sends the two local demo images to Meta. Its output is stored in
`outputs/meta-live-check.json`; it does not create or confirm a complaint.
Use `--original` / `--suspect` to select other test images.

`COMPARER=meta` with no key returns `503 meta_not_configured`, never a silent local
fallback. Authentication, billing, rate limits, malformed output and timeouts have
separate sanitized errors. Failed analysis does not save a claim.

## Meta contract and model

Verified against official documentation on 2026-10-27:

- [Image understanding](https://dev.meta.ai/docs/image-understanding)
- [Chat completions](https://dev.meta.ai/docs/protocols/chat-completions)
- [Structured output](https://dev.meta.ai/docs/structured-output)
- [Models](https://dev.meta.ai/docs/models)
- [Pricing](https://dev.meta.ai/docs/pricing-rate-limits)

The server calls `POST https://api.meta.ai/v1/chat/completions` with Standard-mode
`muse-spark-1.3`, two base64 JPEG images and a strict JSON schema. Images are resized
to a maximum dimension of 1280 pixels. Pydantic validates the response.

The result includes visual similarity, evidence, differences, limitations, summary
and a review recommendation. Screenshot text is untrusted data. Face identification,
account ownership and a final fake verdict are excluded from the model task.

Each new claim stores provider/model and structured observations. Overall similarity
retains the existing 80% image / 20% handle weighting. This is not an impersonation
probability. All claims stay `under_review` until a reviewer acts. Older claims stay
readable with an `Earlier comparison` label.

## Limits and observability

Defaults: 30-second HTTP timeout, 2 attempts maximum, 2048 completion tokens maximum,
50 provider attempts/hour globally and 10/claimed owner/hour. Limits and the 10-minute,
128-entry analysis cache are process-local. Use one API worker when relying on them.
Per-owner identity is unverified; the global cap bounds spend.

Logs record model, prompt version, latency and token counts, not keys, screenshots or
full responses. Standard mode is the default; Contributor models are refused for
profile evidence. Screenshots go to Meta only in Meta mode.

Published Muse Spark Standard prices are $1.25/1M input and $4.25/1M output tokens.
At an **assumed, unmeasured** 3000 input + 500 output tokens/report, 1000 reports cost
about **$5.88**, excluding retries. Actual image/reasoning usage requires live calls
and is recorded in `analysis.usage`.

## API

Reviewer endpoints require `X-Admin-Token`; an unset server token returns 503.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/analysis/status` | Provider/model/readiness; never the key value |
| POST | `/claims` | Multipart owner, suspect, original, suspect_image |
| GET | `/claims?handle=...` | Reports for a suspect account |
| GET | `/statuses` | Strongest visible status; confirmed beats under_review |
| GET | `/claims/pending` | Reviewer queue; token required |
| POST | `/claims/{id}/status?status=...` | Reviewer decision; token required |

Images are limited to 5 MB and 16 megapixels each. Reviewer decisions are independent
of the model recommendation. Neither evidence nor account ownership is verified.

## Tests and live evaluations

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd mobile
flutter analyze
flutter test
```

Tests isolate the real JSON database and use HTTP mock transport for Meta. Passing
proves the client contract and error handling, **not** the model's accuracy.

```powershell
# List 15 cases without API calls.
.\.venv\Scripts\python.exe evals\run.py
# Explicitly send generated synthetic screenshots to Meta.
.\.venv\Scripts\python.exe evals\run.py --live --limit 15
```

The live smoke check passed; the full 15-case live evaluation suite has not run.
Cases cover cloning, unrelated
profiles, fan/parody disclosures, unreadable evidence and screenshot prompt injection.
Results, token counts and latency are saved to `outputs/meta-eval.json`.

Storage is a single JSON file with atomic replacement and an in-process lock. Separate
API and Gradio processes can overwrite each other; use one writer.

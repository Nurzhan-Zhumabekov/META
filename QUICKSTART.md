# Run MirrorCheck from a clean checkout

Unofficial Instagram-style web prototype. Use fictional profiles and local
loopback access. The archive under `mobile/` is the older Flutter client; Flutter
and an Android emulator are not required for the web application.

## Windows: local web and ML

Prerequisites: Git, Python 3.12 or newer, Node.js with npm. The development
checkout was verified with Python 3.14 and Node.js 24.11.1; the OCR/privacy workers
use separate Python 3.12 environments.

```powershell
git clone https://github.com/Nurzhan-Zhumabekov/META.git
cd META
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
Push-Location web
npm ci
Pop-Location
.\scripts\run_web.ps1 -Rebuild
```

Open http://localhost:8090/. The launcher installs both bundled JSON models into
`outputs/ml/` only when those runtime files are absent. Existing trained models
are preserved. New clones start with no complaint records or reviewer decisions;
the walkthrough is a replay of the completed fictional development run, not a
preloaded live claim database.

`COMPARER=local` in the example environment provides labelled local comparison
without a Meta API key. It must not be presented as Meta output.

## Full OCR, image deduplication, Presidio and live Meta

Install `uv` from its official distribution, then:

```powershell
.\scripts\setup_evidence_tools.ps1
```

This installs separate workers using pinned top-level requirements, CPU PyTorch,
and the official spaCy model wheel. OCR models download on first startup. The
dependency lock snapshots are supplied for inspection; the setup script installs
the documented pinned top-level packages rather than silently forcing conflicting
PyYAML requirements into one environment.

Edit the ignored `.env` locally:

```dotenv
COMPARER=meta
META_API_KEY=your_own_server_side_key
META_MODEL=muse-spark-1.3
ADMIN_TOKEN=your_own_long_random_reviewer_secret
```

Never commit these values. Restart the web backend after changing configuration.
`run_web.ps1` starts loopback workers when both environments exist. It will not
replace an already-running server automatically. Stop only the process you
started if you need to restart it.

Check readiness at http://localhost:8090/api/analysis/status and with:

```powershell
.\.venv\Scripts\python.exe scripts\verify_meta.py
```

The readiness check does not call Meta. Submitting a report in Meta mode does send
processed images to the provider and consumes the configured account's quota.
Privacy-tool failure blocks that external image request. Detector misses remain
possible; inspect the masked previews. A separate reviewer action is required to
confirm a report.

## Other operating systems

The core web/API is portable Python and Node code; the supplied worker launchers
are Windows PowerShell scripts. For a core local comparison demo:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python scripts/install_demo_models.py
cd web
npm ci
npm run build
cd ..
.venv/bin/python -m uvicorn src.web:app --host 127.0.0.1 --port 8090
```

Full worker setup on other operating systems requires the same isolated worker
environments and authenticated worker configuration; it was not verified during
this publication. This is a single-writer local demo, not a public deployment.

## English presentation

- `submission/PROJECT_DESCRIPTION_EN.md`: ready English description and short variants.
- `submission/DEMO_VIDEO_SCRIPT_EN.md`: three-minute shot list and exact voiceover.
- `submission/VOICEOVER_EN.txt` and `submission/CAPTIONS_EN.srt`: recording aids.
- http://localhost:8090/english-report-walkthrough.html: actual recorded fictional run.

The existing still captures show evidence, results and the saved decision. The
moderator action button is outside the supplied crop; the script explicitly
labels that transition instead of fabricating click footage. No final narrated
video has been recorded or uploaded by this publication step.

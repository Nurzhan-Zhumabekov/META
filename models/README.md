# Bundled demonstration ML models

These small JSON artifacts let a fresh source checkout run the same independent
inference as the verified local demo, without downloading the raw historical
dataset or executing an upstream notebook.

| Artifact | Role | Limitation |
| --- | --- | --- |
| `profile_risk_model.json` | `profile-logreg-v2-no-avatar`: historical profile fake/spam patterns | Not an impersonation detector or identity probability; excludes avatar presence |
| `pair_risk_model.json` | `pair-text-logreg-v2-synthetic`: text reuse between two explicit profiles | Synthetic training; real-world performance unvalidated |

Install them into the ignored runtime directory:

```powershell
.\.venv\Scripts\python.exe scripts\install_demo_models.py
```

The Windows web launcher runs this step automatically. Existing files under
`outputs/ml/` are preserved, including a developer's own trained models. The
installer never replaces them or writes report records. Other platforms can run
`python scripts/install_demo_models.py` before starting the backend.

For inference, the regular API dependencies suffice; scikit-learn is needed only
to retrain. Training and provenance details, including the profile-data licensing
uncertainty, are in `ML_INTEGRATION.md` and `NOTICE.md`. No raw training rows or
real account identifiers are included in these parameter files.

Version 0.13 bundles v2 of the synthetic text model, selected on an external-text
validation challenge. On its controlled held-out test it detects 92/100 text-copy
pairs (v1: 62/100), with 0/100 negative pairs flagged. This is not independently
labelled Instagram accuracy. See `docs/INDEPENDENT_EVALUATION.md` for provenance,
confidence intervals and the separate photo-region results. Existing runtime
model files are still never overwritten by the installer; back up custom models
before explicitly choosing to replace them with the bundled release.

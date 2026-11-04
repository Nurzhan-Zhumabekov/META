# Public repository preparation

Scope authorized by the owner: publish the current application and the prepared
hackathon materials to `Nurzhan-Zhumabekov/META`. The destination is already
public; no visibility change or history rewrite is required. The repository was
empty before publication.

## Findings and actions

- No known server key, worker key, private-key block, GitHub token, AWS key, Slack
  token or embedded database password was detected in 269 candidate source files.
  This was a scoped local scan, not a claim that every possible secret pattern
  was covered. No existing Git history was present. Dedicated Gitleaks/TruffleHog
  scans were unavailable in the initial environment.
- Credentials and local records are under `.env` and ignored `outputs/`; they are
  excluded. Generated Gradle, Flutter, Python and Node artifacts are excluded.
- New Git commits use the authenticated account's GitHub noreply address.
  Third-party copyright/contact notices are preserved. A dummy URL credential
  in a provider validation test is an inert fixture, not a real account.
- Add MIT for original code and preserve separate third-party/media/dataset terms
  in `NOTICE.md`. Raw mirrored training CSVs are not published.
- Bundle only the two reviewed JSON inference parameter files under `models/`.
  Install missing runtime copies without replacing local training outputs.
- Keep local complaint records private. Publish the already-prepared fictional
  screenshots and English demonstration, with their replay/ownership limitations.

## Acceptance checks

1. Regression tests prove fresh model installation, idempotency, no overwrite and
   validation before partial installation.
2. Run backend/frontend tests and the web production build on the staged source.
3. Inspect the exact Git index for secrets, unintended runtime paths and large files.
4. Publish without force-push, then verify the remote commit and clean-clone core
   inference/build behavior. Final hackathon submission and video upload remain
   separate actions.

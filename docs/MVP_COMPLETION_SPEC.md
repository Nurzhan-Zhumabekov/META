# MirrorCheck evidence and release sprint

Goal: make the demonstrated workflow independently measurable, reviewable and deployable.

Scope:
- Import permitted labelled account pairs through a documented manifest; freeze an account-disjoint test set and report Meta, text ML and their combination separately.
- Add durable moderator reasons, a private decision history, capability-protected appeals and explicit appeal resolution.
- Use transactional SQLite storage with an idempotent import of existing JSON records and unchanged evidence files.
- Prepare an isolated public demonstration, health checks, deployment configuration and current English presentation material.

Non-goals: changing the real Instagram service, asserting account ownership from screenshots, inventing real-world evaluation results, publishing private datasets or creating paid infrastructure without an agreed cost.

Acceptance:
1. Tests reproduce missing-reason, concurrent-write, unauthorized-history, leaked-appeal-access, stale-decision and appeal-transition failures before implementation.
2. Moderator confirmation/dismissal stores a reason and timestamp. An appeal retains the warning while pending; an explicit overturn removes that claim's warning.
3. An unauthenticated caller cannot read the journal or create appeal access. Appeal tokens are hashed at rest, scoped to one report, expiring and absent from public claim responses and logs.
4. Existing reports and evidence are preserved; legacy decisions are identified as having no recorded reason.
5. Evaluation rejects overlapping accounts and duplicate test content, records data/model/input hashes and never tunes on the test set. Missing data or provider results remain visibly incomplete.
6. A deployment is called live only after remote health and an isolated browser workflow pass. Development tests are reported separately from detector accuracy.

Implementation order: storage and decision API -> appeal API -> English reviewer/appeal UI -> dataset audit and evaluation -> deploy and browser verification -> update submission evidence.

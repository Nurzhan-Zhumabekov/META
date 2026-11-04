# Profile ML v2 and pair comparison

Goal: remove avatar dependence from standalone profile risk and add a trained,
independent comparison of two explicitly supplied profiles for copied content.

Scope: retrain the historical fake/spam classifier without profile_pic; retain its
v1 artifact and report both models on the same non-overlapping holdout. Add a
separate logistic model for pairwise text reuse, explicit original-profile input,
API validation, report/reviewer display and reproducible evaluation.

Non-goals: identify people, verify ownership, scrape Instagram, auto-confirm a
report, or claim real-world clone accuracy from synthetic training/evaluation.
No real paired labels are available in the existing historical CSV dataset.

Acceptance: flipping only has_profile_picture leaves v2 risk exactly unchanged;
copied distinctive bios/names rank above unrelated/common-name pairs; fan/parody,
generic bios, empty facts and self-pairs are handled conservatively. Missing
original facts never invent a pair result. Existing clients remain compatible.
Pair training, validation and holdout identities stay disjoint; the existing 15
cases are excluded from training and remain a development regression suite.
All new complaints stay under_review; preserve existing complaints and secrets.

Plan: failing regression tests -> runtime/training slices -> independent evaluation
and original 15 comparisons -> API and web integration -> full tests/build ->
activate local artifacts, restart the owned server, verify UI and publish results.

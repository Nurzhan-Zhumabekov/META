# Profile ML + Meta evidence integration

Current frontend (2026-11-02): native React web in `web/`. Its report form and
reviewer queue use the same validated ML contract and separate ML from Meta scores.
Earlier Flutter-specific notes below describe the original integration; Flutter is
now a legacy client. See `README.md` for current web launch instructions.

## Current ML v2 on 2026-11-03

Version 0.6.0 adds two explicitly separate tasks:

- `profile-logreg-v2-no-avatar`: eight-feature historical fake/spam classifier.
  `profile_pic` is excluded from fitting and inference; toggling only the avatar
  flag cannot change its output. v1 remains available in outputs/ml/v1.
- `pair-text-logreg-v1-synthetic`: learned comparison of explicit original and
  suspect name, bio and handle. Features cover name/handle similarity, meaningful
  bio overlap, shared contact/domain, name+bio interaction and fan/parody disclosure.
  Avatar presence, counts, screenshots and Meta outputs are not features.

The pair model uses 3,120 fictional training pairs, 780 validation pairs and 780
holdout pairs with distinct account identity families and vocabulary pools.
Regularization is selected by five-fold grouped CV on train only; the operating
threshold 0.7 is fixed before holdout evaluation. Runtime JSON inference matches
sklearn exactly on all three splits. No original 15-case input is used for fitting.
On the synthetic holdout it flags 300/300 intended copies and 0/480 negative pairs.
Because the generator is shared and 204 holdout feature vectors also occur in
train, this is a development result, not evidence of real-world clone accuracy.

The historical v2 comparison uses the same 118-profile holdout as v1: accuracy
88.98% versus 91.53%, ROC-AUC 0.9724 versus 0.9828, FP=9 versus 6, FN=4 in both.
The avatar-invariance guarantee is a deliberate tradeoff, not an across-the-board
accuracy improvement on the older spam task. Model selection did not use these
test scores; they are reported with the tradeoff visible.

The previous default-avatar development candidate drops from 71.30% to 6.38%
standalone risk, and its pair copy signal is 0.62%. Five copied-profile cases
score 87.79–94.15% on pair reuse. Avatar counterfactuals match exactly on all 15
cases and through the running HTTP endpoint. A new real Meta+v2+pair smoke report
also succeeded and stayed under_review, in its own database; the real claims file
remains unchanged. The comparison itself replayed the previously recorded Meta
answers without making new Meta calls.

`POST /api/ml/pair-risk` accepts:

```json
{
  "original": {"handle": "owner", "display_name": "Name", "bio": "Explicit original text"},
  "suspect": {"handle": "owner.copy", "display_name": "Name", "bio": "Explicit candidate text"}
}
```

The complaint multipart API optionally accepts `original_profile_facts` with
those three original fields, alongside the existing full `profile_facts` for
the suspect. Handles must match the claimed accounts. Missing original facts
leave pair analysis absent, without fabricating data. Empty bios and self-pairs
return risk_score=null and assessment=insufficient_evidence. Missing/corrupt
models return an explicit 503. All successful complaints remain under_review.

The web form lets users edit original name/bio and clears them when the owner
handle changes. Result and reviewer views label copy evidence and spam patterns
separately and disclose synthetic training. Copy scores from manually supplied
text can remain high even when images are blank: they do not override Meta's
insufficient-evidence recommendation, and do not establish ownership.

Reproduce with `scripts/train_profile_ml.py --output-dir outputs/ml/v2` and
`scripts/train_pair_ml.py --output-dir outputs/ml/v2`. Add `--download` to profile
training if the pinned local CSVs are absent. Both scripts use the pinned sklearn
version in requirements-ml.txt. Use `evals/compare_ml.py --output` with a fresh
directory to replay all 15, and `evals/ml_report.py` for the frozen comparison HTML.
The server uses outputs/ml/profile_risk_model.json and pair_risk_model.json;
activate candidate JSONs there and restart after validation. Roll back the profile
model from outputs/ml/v1 if required; no claims migration is needed.

## Goal
Add a trained profile-feature classifier alongside existing screenshot comparison
and Meta vision analysis. Keep risk separate from similarity and human decisions.

## Scope
- Audit the complete upstream repository at f8dc984326eded77363e7466060cc7ee6d5d32b6.
- Independently implement training, holdout evaluation and safe JSON model export.
- Validate explicit account facts; never invent numbers by reading image pixels.
- Expose profile-risk inference and attach it to new complaints when facts are supplied.
- Show both image evidence and the independent ML score in Flutter and reviewer UI.

## Non-goals
Automatic account suspension, identity verification, Instagram scraping or production
accuracy guarantees. Meta live calls still require a server-side API key.

## Acceptance
1. Train only on upstream train rows; select hyperparameters by stratified CV.
2. Evaluate the selected model on the untouched test split, reporting errors and limits.
3. Verify exported inference against sklearn; no upstream pickle execution.
4. Keep screenshot similarity and ML risk as distinct values and preserve human review.
5. Pass backend/Flutter regression tests and demonstrate the combined report locally.

## Audit findings
The upstream contains README, a 50-cell Colab notebook, a data dictionary, train/test
CSVs (576/120 rows, balanced labels) and seven unlabeled examples. No trained model,
API, tests, environment lock or LICENSE file is present. All source cells, textual
outputs and all CSV rows were read; notebook code was not executed.

The README mixes AUC and accuracy and inconsistently describes bio length. It lists
validation AUC 0.945 while the notebook's recorded best_score_ is 0.9657. It attributes
overfitting to regularization without an independent experiment supporting that claim.
Warnings are globally suppressed and test data are used repeatedly while discussing
model choices. One-hot encoding is fit independently on each split.

The CSV index must be excluded from features. There are no full-feature train/test
overlaps or missing values; the test split contains one repeated feature vector.
The definitions of len_fullname and sim_name_username conflict with the original
dataset, so the independently trained model excludes these two ambiguous fields.

The likely original source is Bardiya Bakhshandeh's Instagram fake/spammer dataset,
collected in March 2019. Its data card explicitly treats fake and spam as interchangeable,
which does not establish impersonation. It lists CC BY 3.0. Provenance of the mirrored
and relabeled categorical columns is not fully documented. Upstream code is retained
only in the separate _research checkout; no notebook code is copied into the app.

Sources:
- https://github.com/Ajaysagayam/Detection_of_Fake_Accounts_in_Social_Media
- https://www.kaggle.com/datasets/free4ever1/instagram-fake-spammer-genuine-accounts
- https://search.r-project.org/CRAN/refmans/classmap/html/data_instagram.html

Training/model reports live under ignored outputs/ml. Dataset age, sample size, manual
labels, class balance and unknown account identities limit generalization. Group leakage
by person cannot be audited because the CSV contains no account IDs or timestamps.

## Measured result
Independent 9-feature baseline: log1p for skewed counts, StandardScaler and L2 logistic
regression. C is selected from 7 values using five-fold shuffled StratifiedGroupKFold,
grouped by the selected feature vector. Test data are not used for hyperparameter selection.

After projecting to the 9 unambiguous fields, one test row overlaps a training vector
and another repeats a test vector. The conservative holdout contains 118 rows (60 genuine,
58 fake/spam). At the fixed 0.5 cutoff: TN=54, FP=6, FN=4, TP=54. Accuracy 0.9153,
precision 0.9000, recall 0.9310, ROC-AUC 0.9828; bootstrap AUC 95% interval 0.9636–0.9953.
The original 120-row evaluation is retained in training-report.json as well.

These are dataset-specific measurements, not present-day Instagram accuracy. The
prototype does not auto-confirm claims from an ML score. Runtime JSON export matched
sklearn probabilities exactly on all train/test feature vectors in this run.

## Reproduce and run
Install `requirements-ml.txt`, then run:

```powershell
.\.venv\Scripts\python.exe scripts\train_profile_ml.py --download
```

Only pinned CSV files are downloaded. Model and report are written to `outputs/ml`.
The API needs only its regular dependencies; sklearn is used for training, not inference.
`POST /ml/profile-risk` accepts explicit validated profile facts. `/claims` optionally
accepts `profile_facts` as JSON in multipart and stores the result under
`analysis.profile_ml`. Screenshot similarity and Meta analysis retain their own fields.

Flutter prefills editable facts from the built-in demo profile and labels them as
unverified. The user can correct them or turn off ML. Meta remains server-side and
requires META_API_KEY; without it the system runs local screenshot comparison plus ML.

## Local verification on 2026-10-28
The release web build was exercised through the complaint form using the two built-in
demo screenshots and editable profile facts. Claim `f86d9ba2` was saved with screenshot
similarity `0.7403645833`, independent ML risk `0.9577681956` and status `under_review`.
The earlier confirmed demo claim was preserved. The result screen is captured in
`outputs/ml/demo/02-ml-result.png`.

82 backend tests and 11 Flutter tests passed; Flutter analysis and the release build
also passed. After the owner configured billing and created a key, a real Meta smoke
request succeeded on 2026-10-28 with `muse-spark-1.3` (1,419 input / 533 output tokens).
Its validated evidence is stored in `outputs/meta-live-check.json`; `COMPARER=meta`
was activated and the API restarted. The key stays in the ignored server `.env`.
At that time, the full 15-case live evaluation suite had not run; see the current
2026-11-03 evaluation below.

The active Flutter complaint form was then exercised against the restarted API.
Claim `65cb3f21` stores `provider=meta`, model `muse-spark-1.3`, independent profile
ML risk `0.9577681956`, combined screenshot/handle similarity `0.7333333333`, and
status `under_review`. The live claim used 1,419 prompt and 438 completion tokens.
The earlier confirmed demo claim remains intact. Screenshots are in
`outputs/meta-demo/`; hashes and the API snapshot are in
`outputs/meta-integration-verification.json`. The new server key was checked absent
from all 48 web-build files and both server logs.

## Full synthetic evaluation on 2026-11-03

All 15 cases completed with real Meta Muse Spark 1.3 and the unchanged local
profile-logreg-v1 artifact. Meta matched the original allowed recommendations
in 15/15 cases. ML returned a finite score with human review required in 15/15;
the ML result attached by the actual complaint pipeline matched independent
inference in all 15. Every isolated complaint remained under_review and the real
complaints file was unchanged.

ML risk is deliberately not graded against impersonation labels. In this suite,
the default-avatar profile scored 0.7130, whereas copied-profile cases scored
0.1295–0.2512. This reveals why the older fake/spam classifier must remain an
auxiliary signal; these 15 fictional examples cannot establish or fix its
real-world calibration. No model weights, thresholds or expected labels were
changed to make the suite pass.

Before evaluation, the generator was repaired so avatar-only and generic-avatar
cases no longer also duplicate all post thumbnails. Images and explicit facts,
full structured answers, token usage and source/model hashes are preserved under
outputs/evals/baseline-20261103. The interactive report is available at
http://localhost:8090/evaluation-report.html after building web/.

# MirrorCheck evaluation, 5 November 2026

## What was measured

We downloaded public research data rather than claiming that fictional demo cases validate real Instagram moderation. External texts were never used to fit model weights. We froze identities, splits and inputs before selecting a candidate on validation, and inspected test results only after that choice. Results are reproducible locally; aggregate reports are published in `web/public/benchmark-results.json`. Raw profiles and photos stay in ignored `outputs/`.

| Held-out task | Baseline recall | Selected recall | Selected false positives |
| --- | ---: | ---: | ---: |
| Controlled text reuse: 100 positive + 100 negative pairs | 62/100 (62%) | 92/100 (92%) | 0/100 |
| Strongly transformed photo regions: 50 copied + 50 different pairs | 1/50 (2%) | 18/50 (36%) | 0/50 |

The text model's test recall Wilson 95% interval is 85.0–95.9%; the photo matcher's is 24.1–49.9%. Zero observed false positives is not a guarantee: the corresponding 95% upper bounds are 3.7% and 7.1%. Confusion matrices, all denominators, model/input hashes and validation results are in the aggregate JSON.

## External text challenge

Source: [Ayoobi, Shahriar and Mukherjee's LinkedIn research dataset](https://github.com/navid-aub/LinkedIn-Dataset), safely read as CSV from [the PeerJ supplementary dataset](https://doi.org/10.7717/peerj-cs.3182/supp-2). We did not execute upstream notebooks or deserialize pickle objects. CSV SHA256: `11ad526b791670fbe479d37a14be8be8801f55c4eabac20f65a92acf1683b533`.

75 source profiles form 25 identity groups per train/validation/test split. Each source yields eight controlled scenarios: exact text reuse, changed display name, different handle, text with an addition, ordinary unrelated profile, coincidental name, disclosed fan account and disclosed parody. Handles are constructed. There are 600 pairs total and 200 test pairs. The external train partition is reserved and was not used to fit weights. The model was fitted only on our fictional procedural training pairs; v2 adds changed-name and partial-bio cases. Threshold remains 0.7.

These labels describe the intended text-reuse triage scenario. The source does not provide original-copy links for real Instagram complaints. Fan/parody disclosures are contextual negatives in this challenge, not legal determinations. Repeated variants from the same source are correlated, so pair-level Wilson intervals do not establish population generalization.

```powershell
.\.venv\Scripts\python.exe scripts\build_external_challenge.py --help
.\.venv\Scripts\python.exe -m evals.independent --manifest outputs/independent-eval/external-text-manifest.json --split test --out outputs/independent-eval/new-text-test.json
```

## Photo-region challenge

[INRIA Copydays](https://thoth.inrialpes.fr/~jegou/data.php.html#copydays) provides original holiday photos and transformed queries for copy detection. The original and strong archives are downloaded from the Facebook Research VISSL dataset mirror. The first 100 source blocks, ordered by a fixed SHA256 rule, are split into 50 validation and 50 test groups. Each group contributes one positive and one negative screenshot pair. Six-photo grids have a controlled layout; correct positives must localize the expected copied region (IoU > 0.7), rather than match a distractor.

Source images are resized to at most 1200 pixels and JPEG quality 92 before grid rendering. Original archive hashes and the full frozen manifest stay in ignored outputs. The validation-selected candidate retains the old pHash/dHash/correlation thresholds and adds mutual ORB/SIFT feature matches, RANSAC homography, inlier and coverage checks. Validation recall rose from 4/50 to 29/50; the lower held-out result above is reported without retuning on test.

```powershell
.\.venv-vision\Scripts\python.exe -m evals.photo_benchmark --split test --matcher baseline --out outputs/independent-eval/new-photo-baseline.json
.\.venv-vision\Scripts\python.exe -m evals.photo_benchmark --split test --matcher current --out outputs/independent-eval/new-photo-current.json
```

The frozen baseline implementation is preserved in `evals/photo_baseline.py`. A fresh machine must download the two Copydays archives into `outputs/public-data-research` before preparing a manifest. Image reuse does not verify identity or account ownership. Strong cropping, tiny post regions, repetitive textures and unreadable evidence remain failure cases. A missing match cannot clear an account automatically.

## Meta and moderation boundaries

Meta and hybrid results for the full external corpus are explicitly `not_run`. The existing live Meta demo and contract tests are separate evidence, not external benchmark accuracy. The evaluator accepts only Meta results bound to the exact profile-pair input hash and reports coverage separately. A full independently human-labelled Instagram corpus is still needed before making real-world moderation accuracy claims.

AI estimates visible reuse. Only an explicit moderator decision, with an explanation and current report version, changes a warning. An appeal keeps that warning until a moderator upholds or overturns it. Account ownership verification, independent annotators and production-scale adversarial evaluation remain outside this prototype.

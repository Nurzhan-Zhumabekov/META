# Meta + profile ML evaluation

Goal: run all 15 existing scenarios against the real configured Meta provider and
the exported profile model, inspect mistakes, repair reproducible defects and rerun
affected cases or the complete suite after a prompt change.

Scope: fix contradictory synthetic fixtures, supply explicit profile facts, preserve
the original recommendation expectations, retain full structured results, usage,
latency, input/model/prompt hashes and isolated pipeline claims. Do not modify the
real complaints database or automatically confirm any evaluation account.

Acceptance: 15 completed Meta results and 15 independent ML results; schema-valid
finite scores; all successful pipeline claims remain under_review; recommendation
checks and ML execution/contract checks are reported separately. ML risk is not
graded against impersonation labels. Synthetic cases are development evaluations,
not independent accuracy evidence. Keep a frozen baseline and every later run.

Plan: add failing fixture/runner tests; correct generated inputs; run a frozen
baseline; inspect every failure; add regression tests and fixes; rerun; publish a
local HTML table and JSON report with honest remaining limitations.

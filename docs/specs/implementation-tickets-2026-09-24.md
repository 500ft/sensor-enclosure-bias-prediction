# Implementation tickets (WP4, 2026-09-24)

**Status: specifications, not implementations.** Each ticket gives affected files, an input/output
contract, **meaningful failure cases** (a test that cannot fail is not a test), and the evidence that
would close it. **None may be implemented without an approved PR**, and none closes an owner gate.

Three tickets from the critique are **already done** and are recorded here for traceability:

| Done | Where |
|---|---|
| `eps` input consistency in `doe_samples` | PR #34 — `theta_full` ignored the `eps` argument |
| Exact nonlinear dimensionless diagnostic | PR #34 — `nondimensional.balance_residual` |
| Non-singular normalisation | PR #34 — `balance_residual_nonsingular`, valid when `T_sky >= T_air` |
| **T2** uncertainty computation | PR #38 — `analysis/uncertainty.py`, 25 known-answer tests |
| **T1** campaign manifest and pairing | `analysis/campaign_manifest.py` — all seven failure cases exercised; see the T1 status note below |

---

## T1 — Campaign manifest and cross-variant pairing

**Affected:** new `analysis/campaign_manifest.py`; `analysis/tests/test_campaign_manifest.py`.
**Must not touch:** `analysis/colocation_intake.py` (the validated single-pair intake stays
byte-compatible; a compatibility test proves it).

**Input:** a manifest file (fields fixed in `pilot-design-2026-09-24.md` R2.2) plus the per-variant
CSV and metadata paths it names.
**Output:** a pairing report — per-arm coverage, **per-contrast** valid-timestamp sets, all-arm
complete cases, and a missingness summary keyed by temperature and power state.

**Failure cases the tests must exercise (each must fail loudly, not degrade):**
1. A manifest naming a CSV whose recorded `csv_sha256` does not match the file on disk.
2. Two arms whose declared cadence or intended window differ.
3. A timestamp present in one arm and absent in another — must be **dropped from the cross-variant
   contrast and counted**, never back-filled or interpolated.
4. A missing optional arm — **degrades to the contrasts that remain valid and reports reduced
   coverage.** *(Corrected 2026-09-25: this must NOT be a loud global failure; a valid V0/V0P
   contrast survives an absent optional arm.)*
5. A duplicate `variant_id`. **`campaign_id` reuse is only detectable against a declared registry
   or scope** *(corrected 2026-09-25)* — so the ticket must define that registry, or the check is
   scoped to "unique within this manifest" and says so.
6. `protocol_commit` absent, **or not resolvable in the declared repository** — a SHA is meaningful
   only relative to a named repo. An offline archive must supply a documented equivalent
   integrity/protocol reference instead; that route is admissible, not a failure.
7. Refusal to overwrite an existing pairing report (follow the rehearsal's refuse-before-write).

**Evidence to close:** the report on a synthetic three-arm campaign; the seven failures above
demonstrated; the existing intake regression suite unchanged and passing.

**Status (2026-09-29): implemented** in `analysis/campaign_manifest.py`
(`python -m analysis.campaign_manifest MANIFEST --out REPORT`). Choices the ticket left open:
- Failure 5: `campaign_id` uniqueness is scoped to **within one manifest**, stated in every report; no
  registry exists, so cross-manifest reuse is not detectable.
- Failure 6: a git SHA needs `protocol_repo` and must resolve there; the admissible offline route is
  `protocol_archive_sha256` (64 hex characters).
- Failure 4: an arm is optional only if the manifest says `optional: true`; optional permits an absent
  file, never a corrupt one.
- Per-arm `cadence_s` / window declarations are accepted only when they equal the campaign's.
- Off-grid, out-of-window, naive-clock and duplicate timestamps refuse; nothing is rounded or filled.

**Not delivered, and why:** the ticket's missingness summary "keyed by temperature and power state".
Power state comes from the auxiliary channels (T3), which do not exist, so missingness is keyed by
channel (absent row / empty sensor / empty reference). Add the power-state key when T3 lands. Coverage is
reported, not judged: no pass/fail against the protocol's readiness criteria is applied here.

---

## T2 — Uncertainty computation

**Affected:** new `analysis/uncertainty.py`; `analysis/tests/test_uncertainty.py`.
**Scope (corrected 2026-09-25): a small linear covariance calculation — not a symbolic metrology
engine.** No distribution inference, no free-text equation evaluation, no Monte Carlo.

**Input:** values `x`, an explicit sensitivity vector `c` (or Jacobian `J`), standard uncertainties
or a covariance matrix `Sigma`, units, and provenance. Distribution and evaluation method are
**documentation of how `u` was obtained**, never a source from which `u` is inferred.

**Output:** `u_c² = cᵀ Σ c` (multi-output: `J Σ Jᵀ`), with **diagonal variance terms and
cross-covariance terms reported separately** — a covariance term may be negative, so percentage
"shares" are not always meaningful.

**Validation contract:**
- `u = 0` accepted **with provenance** (exact input or deliberate model treatment). Negative or
  non-finite `u` rejected. **A missing uncertainty never defaults to zero.**
- `Σ` must be finite, symmetric, correctly dimensioned, non-negative on the diagonal, and **positive
  semidefinite within a declared tolerance**. Pairwise `r ∈ [-1,1]` is necessary but **not
  sufficient**. Physically required **singular** matrices are preserved, not rejected.
- A shared reference is **the same input node**. For `y1 = A−R`, `y2 = B−R`, the contrast `y1−y2`
  cancels `R` **algebraically** — not because a rule says so, and **other errors do not cancel**.
- Distinct references or time slots do **not** make a difference invalid: use the declared
  covariance model, and refuse only the **unsupported automatic-cancellation shortcut**. Never
  silently reuse the identical-reference formula.
- Standard uncertainty is always reportable when well-defined. `U = k·u_c` requires an **explicit
  coverage-factor basis**; with none, report `k` and `U` as *supplied* and leave the probability
  **unspecified**. **Never assert 95 %.** One Type B contribution does **not** invalidate `k = 2`
  nor imply few degrees of freedom.

**Known-answer fixtures (documented, not copied from the implementation):**

| # | Case | Expected |
|---|---|---|
| 1 | A, B each `u=0.1`, R `u=0.2`, independent | absolute bias `√0.05 = 0.2236068`; difference `√0.02 = 0.1414214` |
| 2 | Two unit inputs, `r = 0.5` | sum `√3`; difference `1` — pins the covariance **sign** |
| 3 | Ten resistors `u=0.1 Ω`, perfectly shared calibration | sum `1 Ω`; independent `√0.1 = 0.3162278 Ω` (GUM basis) |
| 4 | `u=0` with provenance | accepted; negative / NaN / inf / missing rejected; singular shared-reference `Σ` accepted |
| 5 | Symmetric `Σ` with off-diagonals (0.9, 0.9, −0.9) | **rejected as non-PSD** though each `r` is individually legal |
| 6 | Different-reference contrast | accepted with explicit covariance; automatic common-reference cancellation refused; unit mismatch refused |
| 7 | No coverage-probability justification | output never prints "95 %" |

**Evidence to close:** the seven fixtures pass with documented known answers, and the existing suite
and CI gates stay green.

## T3 — Auxiliary channel ingestion (T/RH, power, extra nodes)

**Affected:** new `analysis/aux_channels.py`; `analysis/tests/test_aux_channels.py`.
**Must not touch:** the intake schema — auxiliary data lives in a **separate instrument file** keyed
to the same timestamps, so `FIELDS` is not widened.

**Input:** an instrument CSV carrying any of: reference RH, sensor RH, their temperatures, measured
voltage and current, and node temperatures from the §1 map of the experiment contract.
**Output:** a validated, timestamp-aligned frame; derived **power `W = V·I`**; derived **vapour
pressure** `e = (RH/100)·e_sat(T)` for both reference and sensor; and a per-interval **state label**
joined from the power/airflow registers.

**Failure cases:**
1. **RH without a matched temperature is retained as a reported measurement** *(corrected
   2026-09-25)* — it is only **vapour pressure that is uncomputable**, so refuse the *derived
   product*, not the raw channel. Derive a product only when its inputs are usable.
2. **Rated** power instead of measured V and I — must refuse. *(Corrected 2026-09-25: a
   **calibrated measured-power channel** is an acceptable substitute for V·I; `rated_w` is not.)*
3. **Sampling declaration required for V·I:** for varying signals `mean(V·I) ≠ mean(V)·mean(I)`.
   The input must declare whether power is instantaneous-then-averaged or averaged-then-multiplied;
   an undeclared combination refuses.
4. An interval whose fan state is `unknown` — flagged **ineligible for the I1 contrast**, retained
   in coverage. **Eligibility and retention are separate concerns.**
5. Timestamps not on the declared grid, or outside the intended window.
6. **Out-of-range readings (RH > 100 %, `e > e_sat(T)`) are preserved with a flag, not clamped and
   not deleted** *(corrected 2026-09-25)*. Supersaturation near condensation is physically
   reportable; the sensor reading is data, the derived product is what gets withheld.
7. Silent unit coercion — units are declared per column and mismatches refuse.

**Evidence to close:** synthetic fixtures for all six; a vapour-pressure round-trip check; and a
demonstration that an `unknown` fan-state interval is excluded from I1 **but still counted** in
coverage.

---

## T4 — Predictor/target-leakage guard

**Affected:** new `analysis/prediction_contract.py`; tests.

Enforces §9.6 of the Study B design. **Corrected 2026-09-25: classify by transitive INPUT
provenance and calibration access — not by whether a variable was "solved".**

A `Re_vent` produced by a **frozen forward solver** consuming only admissible design, property and
environmental inputs is a **derived prediction**, and is admissible. What leaks is a **measured**
target vent velocity, a coefficient **tuned** on the target, or an **observed** target temperature.
The earlier rule would have blocked all CHT output, which is wrong.

**Input:** a predictor graph — each node tagged `design` / `independently_characterised` /
`environmental_observed` / `target_measured` / `target_tuned` / `derived(parents…)`.
**Output:** admissible or refused, naming the offending node **and the path that taints it**.

**Rules:**
- `derived` inherits the worst provenance among its transitive parents — the check is on the path,
  not the node.
- `environmental_observed` is admissible for a **registered conditional** prediction ("given the
  observed forcing"). It must **not** be relabelled a forecast made from pre-deployment weather
  alone — those are different claims and the label must state which.
- Contest B admits target-derived inputs **only** inside the declared calibration allocation.

**Failure cases:** a solver output whose parent is a measured target velocity must **refuse** (the
taint is transitive); the same solver output from design+property+environment inputs must **pass**;
a conditional prediction relabelled as a forecast must **refuse**.

**Evidence to close:** the three fixtures above, each naming the tainting path.

---

## Sequencing

T1 and T3 are prerequisites for handling any real campaign. T2 is needed before any bias is
reported with an interval. T4 is needed before the first transfer claim. **None is on the critical
path until the owner authorises a pilot** — they are specified now so the authorisation decision is
not delayed by unwritten software.

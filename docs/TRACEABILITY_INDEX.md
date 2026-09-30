# Traceability index (2026-09-25)

Links only — **equations stay beside the decisions they support.** Each row answers: *what was
decided, on what requirement, by what analysis, from which canonical inputs, and what would confirm
it.* Canonical inputs are IDs in [`PARAMETER_REGISTER.csv`](PARAMETER_REGISTER.csv); provenance and
evidence status live there, not here.

**Status vocabulary:** `supported` (analysis + inputs both sound) · `provisional` (analysis sound,
inputs unverified) · `unresolved` (blocked on a missing input or decision) · `withdrawn`.

| Decision / claim | Requirement or objective | Analysis (local) | Canonical inputs | Validation | Status |
|---|---|---|---|---|---|
| Dark enclosure heats substantially in sun | characterise the bias to be corrected | [thermal_bias_results.md](../analysis/thermal_bias_results.md) §2 | P-ALPHA-V0, P-APROJ-V0, P-ACONV-V0, P-GSOL, P-HFLOOR, P-HSLOPE | none — no physical data | **provisional** (P-ALPHA-V0 contradicted; areas lab-required) |
| Painted control V0P is the right comparator | avoid an unmatched shield claim | [matched_control_sensitivity.py](../analysis/matched_control_sensitivity.py) | P-ALPHA-SH, P-ALPHA-V0 | I4 (experiment contract) | **provisional** — real paint moves `eps` too, so an α-only change is a *model* intervention |
| Shield advantage is **not robust** to combined assumptions | decide whether a shield claim is safe | [thermal_bias_results.md](../analysis/thermal_bias_results.md) A3 §; C-ADV-NOM, C-ADV-COMB | P-PHI, P-CBOOST, P-PREHEAT (**all UNCITED**) | I2/I3 | **provisional** — the reversal is driven largely by uncited inputs, which is precisely why they are measurement priorities |
| Model reduces to five dimensionless groups | organise the balance; enable transfer | [studyA_nondimensional.md](studyA_nondimensional.md) §2 | P-TAIR, P-TSKY (fix `tau`) | exact-balance residual C-BALRES | **supported** (algebraic, at fixed `tau`) |
| Dimensionless similarity was **never falsified** | correct a withdrawn claim | [studyA_nondimensional.md](studyA_nondimensional.md) §5; `ExactBalanceTests` | C-BALRES | regression test, 1,944 points | **supported** |
| Linearised law degrades at large bias | know where the approximation fails | [studyA_nondimensional.md](studyA_nondimensional.md) §5 | T-APPROX (exploratory band) | `LinearisationErrorTests` | **supported** as an approximation statement only |
| Wall conduction is first-order for printed enclosures | justify the open axis | [studyA_nondimensional.md](studyA_nondimensional.md) §3 (worked block) | P-KWALL, P-BI | measure wall `t` and `k` on **our** specimens | **provisional** — `k` is measured on *external* specimens |
| Internal dissipation is the distinctive axis | novelty framing | [PHD_SCOPE_AND_NOVELTY.md](PHD_SCOPE_AND_NOVELTY.md) Erratum 2 | P-QINT-V0, P-QINT-SH, X-AIRSTORM | **I1** controlled power intervention | **unresolved** — no source measures it; ours is not measured either |
| Direction B is the immediate scope | produce useful evidence without new geometry/CFD | [research-direction-2026-09-21.md](research-direction-2026-09-21.md) §4 | — | — | **selected** 2026-09-25 (owner) |
| Night/day contrast does **not** identify self-heating | avoid an invalid causal claim | [pilot protocol](COLOCATION_PROTOCOL.md) R1.1 | P-EPS, P-ACONV-SH, P-FSKY-SH, P-TSKY | counterexample: `Q=0.102972 W` → `−1.2e-8 °C` | **supported** (withdrawal justified) |
| I1 estimates °C per watt | identify the dissipation term | [pilot protocol](COLOCATION_PROTOCOL.md) C2 | P-QINT-V0 | measured V·I + fixed airflow | **unresolved** — owner permission #17, fan independence #18 |
| Shared reference cancels in a simultaneous difference | uncertainty budget correctness | [pilot protocol](COLOCATION_PROTOCOL.md) R3.3; `analysis/uncertainty.py` | T-U95 | 25 known-answer fixtures | **supported** (algebra + tests) |
| `U95 ≤ 0.5 °C` means `u_c ≤ 0.25 °C` | admissibility of any comparison | [pilot protocol](COLOCATION_PROTOCOL.md) R3.2 | T-U95 | GUM G.6.6 conditions must be **demonstrated** | **provisional** — conditions not yet demonstrable |
| Single-node model is adequate | whether the lumped comparison is valid | [pilot protocol](COLOCATION_PROTOCOL.md) C1 | T-NODETOL (**UNRESOLVED**) | commissioning node spread, uncertainty-aware | **unresolved** |
| Any result is fit for purpose | project acceptance | — | T-APPTOL (**UNRESOLVED**) | owner packet row 16 | **unresolved** — no verdict is possible without it |
| Data are admissible for review | intake gate | [COLOCATION_PROTOCOL.md](COLOCATION_PROTOCOL.md) | T-SLOTS, T-PAIRED, T-EXPOSURE | intake CLI + manifest (T1, unimplemented) | **provisional** |
| Universal collapse / kill criterion tripped | — | — | — | — | **withdrawn** 2026-09-24 (PR #34) |
| Night convergence shows solar dominates | — | — | — | — | **withdrawn** 2026-09-24 (PR #35) |
| Shared reference is anti-conservative ~3× | — | — | — | — | **withdrawn** 2026-09-24 (PR #34) |

## What this index shows at a glance

Of the live rows, **three are `supported`** and all three are *algebraic or test-backed* — none is a
statement about physical hardware. **Five are `unresolved`**, four of those on owner input or
measurement. **Nothing in this repository has been validated against a physical measurement of this
enclosure**, and the register records only three `field_measured` values, all of which belong to
**other people's systems**.

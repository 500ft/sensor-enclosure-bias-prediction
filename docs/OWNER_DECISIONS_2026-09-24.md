# Owner / PI decision packet — 2026-09-24

**What this is.** A single answer sheet for the decisions only the owner, the PI, or the data
custodian can make. **The agent may record an explicit owner decision with its
source; it cannot invent approval or missing facts.** Original base: `main`
`5b5ec24`. Current permission and remaining blockers live in the
[owner session record](COLOCATION_OWNER_SESSION.md#current-blocker); dated
triage below is historical except where a decision row links to that record.

**Reuses the existing forms — no third intake form is created.** Send
[`DEPLOYMENT_PROVENANCE_REQUEST.md`](DEPLOYMENT_PROVENANCE_REQUEST.md) for route O1 and work
[`COLOCATION_OWNER_SESSION.md`](COLOCATION_OWNER_SESSION.md) for route O2. Technical detail behind
rows 3–8 is in
[`specs/pilot-readiness/pilot-design-2026-09-24.md`](specs/pilot-readiness/pilot-design-2026-09-24.md).

**Status values:** `open` (no decision) · `pending` (requested, awaiting reply) · `accepted`
(evidence received *and* accepted) · `declined` · `deferred`. A request that has been *sent* is
`pending`, never `accepted` — transmission is not receipt.

## A0. Disposition of all 21 rows (2026-09-25)

The 21 rows mixed **choices**, **missing facts**, **external permissions** and **process events** —
so a blanket "answer these 21" was the wrong instrument. Routine planning choices are now
**selected** under the owner's delegation; the rest are grouped into **four evidence packets**.
**Selecting a scope is not acquiring data, approval or authority.**

**Selected (planning choices, revisable):** #07 simultaneous · #09 separate the new-campaign
dependency from `EN-S02` (reviewed ledger amendment; **not** authority to mark `EN-R03` ready) ·
#10 no new CAD unless inventory names a missing fixture · #11 solver allocation deferred ·
#12 CAD tooling migration deferred · **#13 Direction B now, A conditional** · #14 absolute °C as the
primary approximation metric · #15 keep Python 3.11 today · #20 temperature-only minimum campaign ·
#21 held-out geometry deferred with Direction A · #08 **removed as a standalone row** — consolidated
into the within-unit power intervention (#17/#18).

**Deferred with a trigger:** #01 historical outreach — *not* hidden inside any bulk approval;
#06 protocol freeze is a **process milestone**, executed after scope/equipment/thresholds/permissions
resolve (record approver, date, SHA — today's draft is **not** preregistered).

**Four evidence packets (what is actually still needed):**

| Packet | Rows | Asks for |
|---|---|---|
| **A. Purpose** | #16 | intended use and maximum tolerable T error (with exposure/averaging interval). If unknown → register an **estimation-only** study: report bias and uncertainty, **no fit-for-purpose verdict** |
| **B. Inventory** | #03 #04 #18 #19 #20 | unit/probe/reference IDs and counts, calibration records, **fan-power independence**, position-rotation feasibility, RH reference availability |
| **C. Permission** | #02 #05 #17 | the concrete pilot + **specific load procedure**, site access, and raw-data custody/retention |
| **D. Freeze** | #06 | final protocol/analysis version with recorded prospective acceptance |

Physical progress depends on **receipts**, not on unanswered defaults.

## A. Decisions

*Rows 16–21 added 2026-09-24 from the experiment contract (WP2) and the revised K2 contests.*

| # | Decision | Required evidence | Decision owner | Source / reference | Date | Status | Consequence if left unknown |
|---|---|---|---|---|---|---|---|
| 1 | May the historical-log provenance request be sent? | Identified data custodian + authorised channel | Owner | `DEPLOYMENT_PROVENANCE_REQUEST.md` | — | **open** | `EN-S02` stays blocked; `EN-S09B` cannot start; historical rates stay unverified |
| 2 | Is a new physical pilot permitted **in principle**? | Owner confirmation of PI go-ahead | PI, as reported by owner | [Canonical decision and source](COLOCATION_OWNER_SESSION.md#current-blocker) | 2026-09-29 | **accepted — owner-confirmed, in principle** | In-principle permission no longer blocks progress; campaign readiness follows the linked record |
| 3 | Actual hardware and reference availability | Enclosure units on hand (V0, V0P, V1) + a reference instrument | Owner | pilot spec R1.2 | — | **open** | Number of arms unknown; simultaneity (row 7) undecidable |
| 4 | Calibration records and uncertainty budget | Certificates for every sensor **and** the reference, with stated uncertainties | Owner / PI | pilot spec R3.1 | — | **open** | `U95 ≤ 0.5 °C` cannot be demonstrated; no admissible comparison |
| 5 | Site and data permissions | Site access, mounting permission, data-use and retention terms | Owner / PI | [Canonical disposition](COLOCATION_OWNER_SESSION.md#current-blocker) | 2026-09-29 | **open — partially resolved; see linked record** | Resolve the remaining site-specific and data-use details before new acquisition or disclosure |
| 6 | Which protocol version is frozen? | Git SHA of the protocol at freeze, recorded **before** acquisition | PI | `COLOCATION_PROTOCOL.md` | — | **open** | No preregistration; post-hoc threshold drift becomes possible |
| 7 | Simultaneous, or paired-successive? | Count of instrumentable units from row 3 | Owner | pilot spec R1.2 | — | **open** | Default is **simultaneous**. Paired-successive requires explicit approval **and** labelling of weather/time confounding |
| 8 | Is the optional **unpowered arm (V0-U)** authorised? | One spare enclosure + external logging | Owner | pilot spec R1.1 (D2) | — | **open** | The decisive solar-vs-self-heating separation is not measured; the project's `N_Q` axis stays inferential |
| 9 | Should `EN-R03`'s dependency on `EN-S02` be separated for a **new** campaign? | A reviewed ledger amendment | Owner | `SPRINT_TASKS.csv`; `DAY_PLAN_2026-09-15.md` (A2/O2 ledger-dependency note) | — | **open** | A new, independently provenanced campaign stays blocked behind unrelated historical exports. **Do not bypass silently** |
| 10 | Is CAD work actually needed before the first pilot? | A named geometry/fixture need | Owner | `CAD_TASKS.csv` (all deferred) | — | **open** | CAD stays deferred (the default). Existing apparatus may answer the first question |
| 11 | Is solver/toolchain work funded and authorised? | Allocation for install + verification budget | Owner | `specs/study-b-cht/design.md` §8 | — | **open** | FEA stays a stub; Study B's CHT half cannot start |
| 12 | Adopt the proposed **CAD tooling rewording**? | Owner sign-off | Owner | `specs/study-b-cht/design.md` §6 | — | **open** | `CAD_PLAN.md` keeps the CadQuery + Onshape allocation |
| 13 | Adopt **Direction A or B**? | Owner choice | Owner | `research-direction-2026-09-21.md` §1 | — | **open** | The repo carries two research questions; downstream framing stays ambiguous |
| 14 | Re-register the **approximation-error threshold** from relative 3 % to **absolute °C**? *(reworded 2026-09-24: this is a threshold on linearisation error, not a scientific kill criterion — that framing is withdrawn)* | Owner choice, applied prospectively | Owner | `research-direction-2026-09-21.md` §3; `studyA_nondimensional.md` §5 | — | **open** | A relative band stays ill-conditioned near ΔT → 0 and mismatched to a `U95` acceptance |
| 15 | Bump CI Python ≥ 3.12 to unblock dependabot #27/#28? | Owner choice | Owner | PRs #27, #28 | — | **open** | numpy/pandas bumps stay unmerged. **Caution:** a numerical-library change may alter the byte-exact thermal tables |

| 16 | What is the **application tolerance** for temperature (and RH) error? | The intended use's accuracy requirement, stated before observation | Owner / PI | `pilot-design-2026-09-24.md` R3.5 | — | **open** | The scientific comparison tolerance stays TBD; no result can be called adequate or inadequate |
| 17 | Are **controlled power-state changes** permitted on the hardware? | Permission to alter load states, or to fit a controlled resistive load | Owner | `experiment-contract-2026-09-24.md` I1 | — | **open** | The dissipation term cannot be identified; `N_Q` stays inferential and the project's distinctive claim is unevidenced |
| 18 | Can the **fan be decoupled** from the power state? | Hardware check: does powering down also stop the fan? | Owner | `experiment-contract-2026-09-24.md` I1.4 | — | **open** | I1 estimates a combined heat+airflow effect, not heat alone, and must be labelled as such |
| 19 | How many **independently printed units** are available, and can positions be rotated? | Unit count and mounting positions | Owner | `experiment-contract-2026-09-24.md` §7 | — | **open** | Replication cannot be planned; effect estimates carry no unit-to-unit variance |
| 20 | Is an **RH reference** available? | Independently characterised RH sensor with calibration record | Owner | `experiment-contract-2026-09-24.md` §4 | — | **open** | **Campaign narrows to temperature only**; the RH endpoint is deferred |
| 21 | Is a **withheld geometry family** available for a transfer test? | A design genuinely unlike the training set (not a finish replicate) | Owner | `research-direction-2026-09-21.md` K2 contest A | — | **open** | No no-target-calibration transfer claim is possible; only contest B remains |
## B. Inputs only a measurement can close

These are **not** decisions and cannot be answered from a drawing, a datasheet or the literature.
They are listed so they are not mistaken for open questions awaiting an opinion.

| Quantity | Why it must be measured |
|---|---|
| **Internal electrical input power (W)** at the enclosure | *No source located in this repository's search record* reports a measured internal dissipation for a low-cost AQ enclosure with the bias attributed to it — a statement about the search record, **not** a claim that none exists. `shlipak2025` brackets 1–5 W but **estimates** from rated input. `N_Q` depends on measuring it here |
| Wall thickness and material conductivity per printed variant | Printed `k` differs from handbook values, and is anisotropic (~1.6×) |
| **Solar absorptance `alpha` and emissivity `eps` per finish** | **No measured `alpha` for a printed wall exists in any source found.** Colour name is not evidence |
| Vent count, dimensions and open area | Ambient wind is **not** vent velocity |
| Enclosure geometry (`A_proj`, `A_conv`, sensor stand-off) | `A_conv` is an *effective coupled* area, not total CAD surface |
| Sky/long-wave condition during the campaign | The fixed 20 K sky depression is unsupported. **Dewpoint alone does not determine effective sky temperature under cloud** — prefer measured long-wave, else a documented sky model with cloud information and stated uncertainty; log dewpoint as an input to that model, not as the answer |

## C. What is already decided and needs no new ruling

- Data mapping: **one CSV per variant plus a campaign manifest** (pilot spec R2.1); the existing
  single-pair intake is preserved unchanged.
- Data-readiness thresholds: **quoted from the existing protocol**, not redefined.
- No fan arm is proposed **as a scope choice for the minimum campaign — not a finding that aspiration is ineffective.** `shlipak2025` tested *internal recirculation*; `deford2025` aspirates fresh air across an isolated probe, a different arrangement (experiment contract I6). Keep an independently characterised reference either way.
- The scientific comparison tolerance stays **TBD** until row 4 and an application tolerance exist.
  It will **not** be inferred from any model output.

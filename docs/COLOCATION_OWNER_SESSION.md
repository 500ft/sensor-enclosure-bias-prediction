# Co-location owner session — current decisions and blocker

## Current blocker

Documentation reconciliation, 2026-10-06: the owner-authorized switch handoff
reports funding expected but not received; receipt is unconfirmed here. There is
no confirmed campaign date, rig inventory, reference calibration or protocol
freeze. [E1-E4](OWNER_DECISIONS_2026-09-24.md#e-switch-review-decisions) remain
unanswered or unresolved. In-principle PI approval does not answer them.

[PR #56 remains on HOLD](results.md#transient-result-on-hold). Its numerical and
provenance corrections require a separately activated implementation task and
parent review. This documentation task does not authorize physical work.
Direction B and estimation-only reporting remain selected; I1 is mandatory as
the first mechanism experiment. The owner next confirms the PI/rig/funding
inputs and, separately, whether to adopt Direction A with Guibaud.

**Public-data decision, 2026-10-04:** the owner authorized an external-data
suitability study before physical validation. The executed
[AQ-SPEC probe](../analysis/aqspec_feasibility.md) obtained reports but no paired
sensor/reference temperature series with established reuse terms. The owner can
review its draft data request; no outreach has been sent. External comparison
needs a permitted sample and thermal/reference metadata from the data custodian.
This does not close `EN-R03` or establish a transferable design ranking.

**Physical next action:** the owner books the PI date and sets up the
co-location rig at the test site: the enclosure variants, the reference
thermometer in its shield, and the
loggers. No pilot data is collected until the rig exists and the
[protocol](COLOCATION_PROTOCOL.md) is frozen.

**Owner statement, 2026-09-30:** "for enclosure there are currently no
co-location logs at all. but they will be setup in the future, thus the data
collected today is not worthwhile." That statement left no existing
thermal co-location evidence to review, so the retrospective-review route recorded on 2026-09-29 was closed,
and the pilot will be a new acquisition under a frozen protocol.
The public-data decision permits external suitability work;
any historical lab alternative still needs PI data terms and hardware/exposure
metadata. No historical logs or permissions have been supplied.
`EN-R03` stays blocked until that acquisition has happened and passed intake.

**Decisions recorded 2026-09-30** (owner-delegated, revisable until the
freeze): estimation-only reporting, the I1 test permitted with a resistive
load, a 14-day maximum campaign window, historical outreach deferred. See the
[decision table](OWNER_DECISIONS_2026-09-24.md#a00-decisions-recorded-2026-09-30).
These decisions remain in force; the external-data step does not freeze the
physical protocol.

This supersedes the 2026-09-29 notes that the owner had "something like this"
and didn't know where its logs were.

**Owner decision recorded 2026-09-29:** the owner stated in this project session,
"my PI has given me the go ahead with this project. so we have a place to test,
manufacturing to help" and subsequently directed us to move forward because the
blocker was solved. PI permission **in principle** is resolved on that owner
confirmation; test-site availability and manufacturing support are also
owner-confirmed. The PI's name, approval conditions, site details and specific
data-use terms were not supplied. Do not request the same in-principle decision
again, or infer approval of a particular load intervention or protocol version.

This is the canonical current blocker record. The dispositions below separate
resolved permission from still-unverified equipment, data and analysis readiness.
Update this record and review the PR status after every push as specified in
[AGENTS.md](../AGENTS.md#blocker-update-at-every-pr-push--owner-rule-2026-09-29).

## Equipment and evidence review

Originally prepared 2026-09-11; current dispositions supersede that preparation
snapshot. This supplements the historical
[deployment provenance request](DEPLOYMENT_PROVENANCE_REQUEST.md), which remains
open; it does not fill missing register entries with guesses.

Bring the [draft protocol](COLOCATION_PROTOCOL.md), actual device/reference
inventory and calibration records, a proposed site/access permission record,
and the intended acquisition window. Record owner, decision date and supporting
source for each answer; leave missing answers explicitly unknown.

| Decision | Required evidence | Current disposition |
| --- | --- | --- |
| PI permission in principle | Owner confirmation of PI go-ahead | Resolved; source and scope recorded above |
| Site, manufacturing and data terms | Site/mounting details, manufacturing contact/capability, data-use and retention terms | Site and manufacturing support confirmed above; details and data terms not yet supplied |
| Actual equipment and controls | Box/reference IDs, finish/geometry, sensor placement, firmware and heat load | Rig not built yet (owner, 2026-09-30); inventory is recorded when it is |
| Reference quality | Current calibration, aspiration/shield characterization, uncertainty budget and pre/post check method | Blocked; no calibration verified |
| Prospective protocol freeze | Approved version/commit, positions and pairing, intended UTC start/end, cadence, interventions and uncertainty method recorded before acquisition | Draft only; not frozen |
| Acquisition and custody | Authorized operator, raw export location, raw-byte SHA-256, omissions and separate sky/intervention records | No acquisition yet, and none before the rig exists and the protocol is frozen |
| Physical interpretation | Provenance review, corrected as-built model and declared uncertainty treatment; application tolerance only for a later fit-for-purpose verdict | Estimation-only comparison pending physical data; no model-agreement band or frozen prediction exists |

When the rig is built, record its inventory (enclosure IDs, sensors, the
reference and its calibration certificate), then accept or amend the draft
protocol, freeze it before the first acquisition, and name the operator. Record remaining decisions with date and source.
General project approval does not establish a prospectively frozen protocol.

After authorized acquisition, run from the repository root:

```sh
python -m analysis.intake_gate CSV_PATH --metadata METADATA_JSON
```

Paths are placeholders, not claims that an export exists. Keep private raw data
out of git and preserve original bytes. Retain the JSON report, exit code, CSV
and metadata hashes in the authorized evidence store. Exit 2 requires input or
coverage investigation without deleting unfavorable observations; exit 3 is
synthetic-only. Exit 0 admits a physical-labeled pilot for human provenance review
and **does not validate the model**. Metadata labels can be falsified; a hash only
binds bytes. No software test authenticates measurements or closes EN-R03.

Do not derive acceptance bands from the simulated −4 °C or +8–23 °C scenarios.
If hardware or weather cannot meet the proposed pilot requirements, document a
prospective amendment instead of relaxing thresholds after observing results.

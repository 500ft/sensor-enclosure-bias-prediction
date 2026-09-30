# Co-location owner session — current decisions and blocker

## Current blocker

**Next action:** owner supplies the location of the existing test data and the
sensor/reference setup details, or identifies the logger/lab custodian who can
locate them; agent reviews those records before proposing another acquisition.
The owner reports an existing co-location-like setup, but its logs,
reference identity, calibration and overlapping day/night coverage have not yet
been inspected. This is an access/identification gap, not a finding that no data
exists. `EN-R03` remains incomplete until actual evidence is reviewed.

**Latest location update, 2026-09-29:** the owner replied "i dont know wxactly
where." A bounded check of the repository checkout and its dedicated local CAD
project directory found no physical co-location export. The
[data guide](data-and-figures.md#deployment-log-plots) names historical device
exports but provides only a placeholder directory; those exports are not
established as reference-paired pilot data. Cloud storage, lab systems and other
locations have not been ruled out. The next input is the logger/storage system
or the person holding its exports, not renewed PI approval.

**Owner decision recorded 2026-09-29:** the owner stated in this project session,
"my PI has given me the go ahead with this project. so we have a place to test,
manufacturing to help" and subsequently directed us to move forward because the
blocker was solved. PI permission **in principle** is resolved on that owner
confirmation; test-site availability and manufacturing support are also
owner-confirmed. The PI's name, approval conditions, site details and specific
data-use terms were not supplied. Do not request the same in-principle decision
again, or infer approval of a particular load intervention or protocol version.

The owner also stated, after the pilot explanation, "i definatly have something
like this." Review those existing records first. If acquisition predates a
registered protocol, label that analysis retrospective/exploratory; do not
backdate approval or protocol freeze. A new campaign is needed only for gaps
the evidence review actually identifies.

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
| Actual equipment and controls | Box/reference IDs, finish/geometry, sensor placement, firmware and heat load | Existing setup reported; inventory not yet inspected |
| Reference quality | Current calibration, aspiration/shield characterization, uncertainty budget and pre/post check method | Blocked; no calibration verified |
| Prospective protocol freeze | Approved version/commit, positions and pairing, intended UTC start/end, cadence, interventions and uncertainty method recorded before acquisition | Draft only; not frozen |
| Acquisition and custody | Authorized operator, raw export location, raw-byte SHA-256, omissions and separate sky/intervention records | Await existing data location; acquisition history and coverage not yet reviewed |
| Physical interpretation | Authenticated provenance review, as-built prediction and propagated uncertainty, application tolerance registered before comparison | Blocked; no model-agreement band exists |

First inspect the existing equipment records and raw exports without altering
their bytes. Establish what was measured simultaneously and which conditions
were covered. For any new acquisition, accept or amend the draft prospectively
and identify its operator. Record remaining decisions with date and source.
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

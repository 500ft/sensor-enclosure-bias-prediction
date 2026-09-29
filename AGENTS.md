# Agent instructions

## Scope discipline — owner rule, 2026-09-29

This repository exists to be finished. A PR must do at least one of these:
add a measurement or an executed run, change a result, close an item on the
critical path below, or record an owner decision. If it does none, don't open it.

- **No plan-only PRs.** A plan belongs in the PR that implements it, or in a
  `.txt` handoff outside the repo. Never open a PR that supersedes another plan
  PR; edit the open one.
- **One home per number.** A consequential number lives in one canonical file
  (a results JSON or the parameter register). Other documents link to it and
  don't restate it. If a correction would need edits in more than one document,
  replace the copies with links first.
- **No hardening before first use.** Don't add or extend intake, manifest,
  contract or provenance checkers for data that doesn't exist yet. Build a
  checker in the same PR as the first real data it checks. A fix to a fix
  (`-b`, `-c`) is the signal to stop.
- **No cross-repo template passes.** Don't apply a change here because it was
  applied to a sibling repository (literature reviews, presentation passes,
  audits, traceability indexes) unless this repo's critical path needs it.
- **When blocked on the owner, say so in one line and stop.** Don't fill the wait
  with documents.
- Dependency updates arrive as Dependabot's grouped monthly PRs; don't hand-edit
  pins to chase them.

**Critical path:** review available co-location evidence -> complete any missing
pilot acquisition -> compare the measurements with the model. Read the
[current blocker and owner decisions](docs/COLOCATION_OWNER_SESSION.md#current-blocker)
at the start of every session; that record supersedes dated permission/blocker
statements elsewhere. Do not reopen a resolved gate without new evidence.

## Blocker update at every PR push — owner rule, 2026-09-29

- Before every PR push, reconcile the current blocker in
  `docs/COLOCATION_OWNER_SESSION.md` against owner statements and work actually
  completed. Record a changed disposition, its date/source, the next action and
  who supplies it in the same implementation or owner-decision commit.
- Keep that file the canonical home for the current blocker. Other documents,
  task rows and PR descriptions link to it instead of keeping competing lists.
- After every push, verify the remote commit and PR state, then update the PR
  description with a link to the record and whether the blocker changed or was
  reviewed and remains unchanged. A PR push does not itself close a gate.
- If nothing changed, report that review in the PR; do not create an empty
  commit or a separate status-only PR. If new information arrives after a push,
  amend the same PR with the changed record and verify its next push.
- Record owner-confirmed approval as such. Do not treat it as calibration,
  protocol freeze, acquired data, permission for a specific intervention, or
  physical validation. When the next input is owner-held, name it in one line
  and stop after finishing the authorized PR work.

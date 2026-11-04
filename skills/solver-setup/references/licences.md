# Licensed solvers

Some solvers need a licence: Hexaly, CP Optimizer beyond CPLEX Community Edition, OptalCP,
or Gurobi beyond the pip wheel's size limit. A licence is the user's to acquire, and it
can take minutes to days. **Ask for it as early as possible, and keep working while you
wait.** A running solver is what lets you test and debug, so the licence request comes
first. You stop to wait only when nothing else is left.

The machinery is `evaluation/licences.py` (its docstring has the details):

- The integration declares the licence in `metadata.json`. See [integration files](integration.md#4-metadatajson).
- Each machine configures it outside the repository.
- The evaluator binds it read-only into each run, and redacts it from everything a run
  prints.
- A run the solver refuses for want of a licence is `licence_unavailable`, which never
  counts against a model.

**Never open, print or copy a licence file.** It must not reach a transcript, a log or a
commit. To learn what you need, run the commands below; they never show the content.

| Command | Says |
|---|---|
| `python -m evaluation.licences check ID` | whether licence ID is configured and usable here (exit 0/1), and solves each registered pilot with it |
| `python -m evaluation.licences todo` | every licence still missing, with the steps for the user |
| `python -m evaluation.licences args ID` | the `docker run` flags that give a probe or toy-test container the licence |

## 1. Triage: before any research (step 0b)

1. **Classify** the licence from the solver's install or pricing page or PyPI page. This
   is a few minutes of reading, not the full research:

   | Class | Example | What follows |
   |---|---|---|
   | open source | Choco, OR-Tools | no licence work |
   | free edition, no key | gurobipy wheel (2000 variables), CPLEX Community Edition (1000) | use it; its limits go in `compatibility` and *Common issues*; declare `"without": "size-limited"` only when you also add a full-licence path |
   | key file | Hexaly `license.dat` | `kind: file` |
   | licensed install | CPLEX Optimization Studio (CP Optimizer) | `kind: directory`, the install mounted read-only |
   | licence server | Gurobi token server | `kind: server`; the run reaches it through a relay, never through the network |
   | unusable here | needs internet while running (Gurobi WLS); node-locked to a hostname or MAC address; a named-user licence that refuses containers | **blocked**, with the reason: the evaluator gives no run network or a stable host identity |

   Note any licence term that limits publishing benchmark results. It goes in `LICENCE.md`
   and the report.

2. **Check whether it is already here:** `python -m evaluation.licences check ID`, where
   ID is the licence id you will declare (the solver's name: `hexaly`, `gurobi`). If it
   passes, the run is fully automatic; skip to the normal workflow.

3. **If it is missing, write `solvers/<solver>/LICENCE.md` now**, beside the skill. It is
   for a person and has these parts:
   - **What you need:** the edition, and whether a free trial, academic or community
     licence suffices.
   - **Get it:** the registration URL, academic eligibility and the steps. Prefer the
     quickest route that is good enough to debug with, such as a trial, and name the
     full licence as the upgrade.
   - **What you receive**, and its form: file, install or server details.
   - **Store it:** `~/.config/dcp-rosetta/licences/<id>/`, `chmod 600`, never inside the
     repository.
   - **Configure:** `python -m evaluation.licences set <id> PATH`.
   - **Verify:** `python -m evaluation.licences check <id>`.
   - **Terms:** limits on use, expiry, and publishing.

   It names no machine-specific path and no key.

4. **Ask without stopping.** In your next progress note, give the user the steps from
   `LICENCE.md`: where to get it, and the `set` and `check` commands. If a PushNotification
   tool is available, also send one short notification, because the user may be away.
   Do not use AskUserQuestion here: keep working.

## 2. Licence-pending mode: everything that needs no licence

Carry on with the workflow, doing every step that needs no running solver:

- Research from the docs. Install the package in the image. Probe imports and the API
  without creating an optimizer.
- Write the standalone skill. A claim you could not run is marked
  `unverified: needs a licence` in `sources.md` until you run it.
- Write `Dockerfile` (with no licence in it), `metadata.json` with its `licence`
  declaration, `run.py`, `CONTRACT.md` (a sentence under `## Environment`: the licence is
  bound at `target` with its variables) and `readiness_test.py`, including
  `licence_missing`.
- Build the image, run `check_integration.py ID --static`, and run the
  `licence_missing` check, which needs no licence.

Re-run `python -m evaluation.licences check ID` at each checkpoint: after research,
after the image builds, and before the first solving step. The moment it passes, leave
licence-pending mode and continue normally.

Probes and toy tests that need the licence add its flags to their container:
`docker run $(python -m evaluation.licences args ID) ...`. Evaluations and readiness
bind it themselves.

## 3. When only licensed steps are left

The steps that need the licence are:
- the hello-world and the tiny models of §2.3;
- running `check_assets.py`;
- the toy-problem rounds;
- `generation.readiness check`;
- registering the pilot.

What happens next depends on how you are running:

- **Interactive** (a person started you and AskUserQuestion is available): ask once,
  "Everything that runs without the licence is done; the rest needs the <solver>
  licence. Is it configured?", with the options *configured, continue* and *stop,
  resume later*. On *configured*, run `check` and continue. On *stop*, finish as below.
- **Headless** (called by model-generator, a workflow or another agent, or no one can
  answer): do not ask; finish as below.

**To finish while the licence is still pending:**

1. Write `<integration>/PENDING.md`: a checklist of the deferred steps with their exact
   commands, in order.
2. Put the licence to-do (from `LICENCE.md`) at the top of the report.
3. Send a push notification if one has not already gone out this run.
4. Record `setup_blocked` with the reason `licence_pending`.
5. Return **licence_pending**, not **blocked**: the work is done up to the licence.

## 4. Resuming

Run solver-setup again on the same target. When `<integration>/PENDING.md` exists:

1. Run `python -m evaluation.licences check ID`. If it fails, return **licence_pending**
   again, at once.
2. Do the deferred steps in the order the file lists them, and rerun every step whose
   input changed (any skill edit needs another toy round).
3. Delete `PENDING.md`, and return **ready** once readiness and
   `check_integration.py ID` pass.

## 5. Readiness check `licence_missing`

Required whenever `metadata.json` declares a licence. Run one evaluation of a valid model
with `DCP_LICENCE_<ID>=none` set in the check's environment. The evaluator then runs the
solver without the licence, and the check passes when the result's reason is
`licence_unavailable`. That proves the solver's own refusal message is listed under
`errors`.

Read that message from the failed run. If it is not caught, add a substring of it to
`errors`. Keep each substring specific to licences, so that a model error never matches.

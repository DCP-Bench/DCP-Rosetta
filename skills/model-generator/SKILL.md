---
name: model-generator
description: Populate the DCP-Bench Open repository (submodule `/bench`) with constraint models. Pick an uncovered problem and solver combination, write an instance-agnostic model, verify it against the reference, keep it, and move to the next one. Use this skill for model generation campaigns.
---

# Model generator

Add models to the DCP-Bench Open repository (submodule `/bench`) that a real evaluator has accepted: choose a problem and a solver integration, write a model, prove it holds up, keep it, move on.

You need this repository, a Python environment (`.venv/Scripts/python.exe` on Windows, `.venv/bin/python` on Unix), and a running Docker Linux engine. Run every command from the repository root; all paths here are relative to it. An unavailable engine is a blocker to report, not something to work around: candidate code never runs on the host.

**You are the only agent**, unless the user asks you to coordinate subagents (see [Running a campaign with subagents](#running-a-campaign-with-subagents)). You are the coordinator and the modeller; "invoke a skill" only ever means "read that file and follow it".

What a model must look like comes from three layers, read in this order every time you write one:

| Layer | Where | What it gives you |
|---|---|---|
| The submission contract | `solvers/CONTRACT.md` | What every model must do to be evaluated, for any solver: input, declared outputs, objective, what the runner does, what a model must not do |
| The integration contract | `CONTRACT.md` in the integration's folder: `solvers/<solver>/<interface>/` for id `<solver>_<interface>` | How that integration realises it: file, entrypoint, how the instance arrives, how outputs and the objective go back, its traps, a minimal working example |
| The solver skill | the `skill` path `next_work` reports for the integration, and its `interface` | How to model with that solver: its API and pitfalls. A skill shared by several bindings of one solver routes from its `SKILL.md` to `interfaces/<interface>.md` or `interfaces/<interface>/README.md`: read `SKILL.md` and that interface, nothing of the others. |

The contracts are Rosetta's; the solver skill is not, and knows nothing about this repository. Where a skill and a contract disagree on how a submission looks, **the contracts win**.

Read `skills/solver-setup` when the integration you need does not exist. This skill and `solver-setup` self-improve through the procedure in [operations](references/operations.md).

## The loop

```sh
git switch -c models/<run-id>                       # never commit to main, never push
python -m generation.manage init --run <run-id> --config config.json
python -m generation.next_work                      # what is uncovered, and what is not usable
python -m generation.brief PROBLEM                  # the contract: outputs, objective, fields
python -m generation.manage attempt --run <run-id> --problem P --solver S \
    --skill skills/model-generator --skill <the integration's skill path from next_work> \
    --agent "TOOL (MODEL-ID)"                        # the model that writes this attempt
#   write the model into the attempt directory, following the contracts and the solver skill
python -m generation.manage evaluate --attempt ATTEMPT --model ATTEMPT/model.EXT
python -m generation.manage retain  --attempt ATTEMPT        # only when it was accepted
#   commit each batch of accepted models, then take the next pair
```

1. **Branch first.** The run gets a branch of its own, off whatever branch you
   are on, so its commits can be reviewed, kept or dropped as one unit. Being on
   a branch already does not satisfy this. Use the same `<run-id>` for the
   branch and the run. If the checkout has uncommitted work, stop and ask.
2. **Agree the budget** before generating. Defaults, unless the user says
   otherwise: 10 model attempts per pair, one new integration per run, two setup
   attempts per integration, 60 minutes. Stop starting new work when it is gone,
   then checkpoint what exists.
3. **Set a profile that makes a pass mean something** (below), and freeze it.
4. **Pick the work** yourself unless the user named it. `next_work` lists every
   integration with whether it is usable, the uncovered pairs, and what it is
   withholding; a pair under `unbindable_pairs` is impossible for that
   integration whatever you write, and `blocked_pairs` are recorded dead ends.
   Prefer problems with several instances when you want the evaluator itself to
   catch a hardcoded model. An integration reported as not `ready` cannot be
   used at all; legacy directories under `generated_models/` are not coverage.
5. **Read the contract.** `generation.brief PROBLEM` prints the problem
   description, the declared output names with their shapes, the objective
   direction, and every instance field with its shape.

   **Start blind**: model from the brief, the instance JSON, the two contracts,
   the solver skill and the evaluator's feedback, without opening the reference
   (`bench/dataset/<problem>/<problem>.cpmpy.py`) or other integrations' models. If
   that is not working, read the reference and say so in the attempt's
   `lessons.md`. Never execute its solve tail, never carry over a constraint it
   keeps commented out between `<SYMMETRY_BREAKING_CONSTRAINT_START>` and
   `..._END>`, and never embed an answer, whether computed by running the
   reference or branched on which instance you were given. A missing or
   self-contradictory specification is a reference blocker — record it and move
   on.

   The brief takes every shape from the *example* instance. Other instances can
   be larger or smaller (a board, a number of items, a matrix of classes), so
   take sizes from each instance's own data unless the description fixes them.
6. **Write the model** into the attempt directory: `solvers/CONTRACT.md` for what
   it must do, the integration's `CONTRACT.md` for the shape it takes in that
   integration (start from its example), and the solver skill for the API. It
   must build the model *from* the instance argument. Fixed mathematical
   constants are fine; embedding a known answer is the one failure this whole
   system exists to catch. The attempt cites both skills and both contracts, so
   none of them may change while it is open.
7. **Evaluate through the helper**, which preserves the exact evaluated bytes.
   On a rejection, read `reason` and `detail` and route the failure with the
   table in [the run protocol](references/run-protocol.md). Repair the model and
   open a *new* attempt; never overwrite one, never resubmit unchanged bytes.
   After the attempt cap, mark the pair exhausted and take the next one.

   Iterate first with `python -m evaluation.check MODEL --problem P --solver S
   --instance-count 2 --solution-limit 2 --execution-timeout 180 --reference-timeout 180`,
   which spends no attempt. Pass the run profile's timeouts: the defaults are 60 s,
   and a model that needs longer would look like a failure there. Keep the
   solution limit at 2: a second solution often exposes a reading looser than
   the reference's. Never edit an attempt's files after it was evaluated;
   `evaluate` will not run it again, so read its `evaluation.json` instead.
8. **Before retaining**, satisfy yourself the model is right *and readable*:
   [acceptance](references/acceptance.md) says what the record has to show and
   what only you can check, including the comments a model has to carry. Then
   `retain`.
9. **Commit in batches**, not once per model: a coherent group of accepted
   models in one commit — a sweep of related problems, or one integration's
   share of the run — with a message naming what it carries and any reduced
   coverage among them. Commit a batch before starting a long wait, so accepted
   work is never left uncommitted across one, and again at the end of the run.
   What makes an interrupted run resumable is the ledger, not git: `retain`
   writes `retained.json` and the record under `generated_models/` as it goes,
   and `generation.manage status` reads those back whether or not anything was
   committed.

Independent pairs are independent: nothing stops you writing several models
before evaluating, or running several evaluations at once, as long as each has
its own attempt.

## The profile is the coverage claim

Create the run once, on the branch you made, with `config.json` **inside** the
repository (the helper refuses a path outside it):

```json
{
  "agent": "the run's setup: which models write and which coordinates",
  "budgets": {"integrations": 1, "setup_attempts_per_integration": 2,
              "model_attempts_per_pair": 10, "wall_minutes": 60},
  "profile": {"instance_count": 99, "solution_limit": 2, "tolerate_inconclusive": true,
              "execution_timeout": 180, "reference_timeout": 180,
              "compilation_timeout": 120, "memory_mb": 2048, "cpus": 1}
}
```

`instance_count: 99` is the setting that matters: a count above the supply is a
budget rather than an error, so one number checks every distinct instance of
every problem, and a model that fitted the example dies on the second one. The
cost lands in the right place, since a wrong model fails early and stops.
`tolerate_inconclusive` skips an instance that only times out instead of ending
the pair, and `solution_limit: 2` gives the search a second chance to surface a
wrong solution — drop it to 1 when the integration declares
`enumeration: false`, or the result is `unsupported_capability`.

The profile is frozen for the run. Use one run per integration when capabilities
differ, and never weaken a profile mid-run to turn a failure into a pass.

The run's `agent` describes the run: the tool or harness, which models write
and which coordinates. Each attempt names its own writer with `--agent` as
`TOOL (MODEL-ID)`, using the tool and the model's own identifier, e.g.
`codex (gpt-5)` or `claude-code (claude-haiku-5-5)`. That value is copied into
the retained record and shown on the site as "Generated by". Pass the model
that writes the attempt, even when a pair moves to a stronger model mid-run.
The helper refuses an empty value or `unknown`, and a value naming more than
one model it recognises.

## When something is missing, or teaches you something

- **The integration does not exist, or is not usable.** Both cases are in
  [integrations](references/integrations.md): building one means following
  `skills/solver-setup` yourself and recording the setup skill *before* writing
  any integration file; certifying an existing one whose `readiness.json` is
  missing or stale is a separate, smaller job. Neither is a reason to rebuild a
  working integration.
- **A failure taught you something general.** Put it where the next model will
  read it, with evidence and a reproducer, never on a hunch:

  | The lesson is about | It goes into |
  |---|---|
  | the solver or its API (an API needs integer coefficients, a constraint has another name) | the solver skill, via propose/check/apply in [operations](references/operations.md): its interface file when the lesson is about one binding's API, its `SKILL.md` only when it holds in every binding |
  | how this integration's runner reads a model (an output container it rejects, a shape it mangles) | that integration's `CONTRACT.md`, edited directly with the evidence. The runner's code is the authority, so check the claim against `run.py` |
  | what every model must do | nothing: `solvers/CONTRACT.md` binds every integration, so report it to the user as a proposal |

  Problem-specific insight belongs in that pair's attempt history and nowhere
  else. Record a proposal you decided against, with your reasoning.
- **A pair is not worth attempting again.** Add it to
  `generation/blockers.json` with its evidence, so the queue stops offering it.

## Running a campaign with subagents

When the user asks you to coordinate other agents instead of modelling alone,
you keep the decisions and they do the modelling.

- **Start with the cheapest capable model.** Give each agent about 5-8
  problems, so its context stays under roughly 100k tokens; long contexts cost
  more than extra agents. Move a pair to a stronger model only after the cheap
  one exhausted its share of the attempts, and only with the user's consent.
- **Bound the load.** At most 8 agents at once, each running at most 2
  evaluations at once; more makes timeouts near the limit unreliable.
- **Give each agent a fixed prompt**: the run, its problems, both skill paths
  (this one and the solver skill `next_work` reports), the two contracts, its own
  model id for `--agent`, a working directory of its own, and what to report (a table per problem plus the skill gaps it hit, each with the exact
  error message and the fix).
- **Freeze the solver skill and the integration's contract while a wave runs**
  (an attempt refuses changes to either anyway). A skill shared by several
  bindings is frozen for all of them, also for waves on another binding. Collect the reported gaps in one
  file and apply them between waves, each where the lesson table above sends it:
  the solver skill's development copy, the integration's `CONTRACT.md`, or the
  runner. Before adding a syntax claim,
  confirm it with a tiny model in the solver image; agents report wrong claims
  too.
- **Fix the runner, not the models, when many agents hit the same wall.** Tell
  the running agents to skip such pairs instead of spending attempts on them, and
  bring the integration's `CONTRACT.md` in line with the fixed runner.
- **Audit each wave** before committing it: search the agents' transcripts for
  reference reads their `lessons.md` does not mention and for candidate code run
  outside the container.
- **Leftovers** go to a retry wave (which may read its own run's `lessons.md`),
  then to blockers with evidence.

## Rules that do not bend

- Never edit a reference, the dataset, the evaluator, or the runner to make a
  model pass. If you believe a reference is wrong, record it as a blocker and
  leave it alone.
- Never weaken the profile, skip an instance, or reinterpret a failure to
  manufacture a pass.
- Never call something accepted without an evaluator record that says so. A
  clean build, an empty stderr, and your own reading of the model are not
  acceptance.
- Never overwrite a previous attempt, a retained model, or a legacy directory.
- Never work on a branch you did not create for this run, and never push or
  install skills globally.
- Never touch an integration you are not setting up, and never edit
  `runner/runtime.py` or `runner/requirements.txt` to suit a new one. Both are
  shared with every certified image; a new integration gets its own `run.py` and
  its own Dockerfile dependencies.
- An unavailable Docker engine, a missing licence, or an exhausted budget is a
  concrete blocker to report — not a reason to claim the work is finished.

## Finish

Report: each accepted model with its retained path and the coverage actually
achieved; pairs left exhausted or blocked with the reason; integrations created
or repaired; skill changes applied or left pending; and the budget you used.
Say plainly what you did not verify. If the run was interrupted, checkpoint it
as interrupted — never as complete.

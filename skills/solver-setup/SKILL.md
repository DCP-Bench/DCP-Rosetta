---
name: solver-setup
description: Meta skill to generate solver skills for the DCP-Rosetta project. 1) generates a standalone skill for a combinatorial (optimisation) solver, 2) adds the Rosetta-specific infrastructure (metadata, Docker image, runner, readiness test) to be able to evaluate the standalone solver skill. Use this skill when asked to add a solver skill or indirectly when the model-generator skill needs an intagration that is missing or broken.
compatibility: Requires a python environment, Docker and a DCP-Rosetta checkout
---

# Create a new solver skill

Produce two artifacts: 1) a standalone skill teaching an agent how to model using the interface of a combinatorial (optimisation) solver, 2) infrastructure needed for the DCP-Rosetta framework to evaluate this new skill (Dockerfile, tests, runner, etc). The two must clearly be separated, no details of Rosetta can leak into the independent solver skill, that skill should be sharable publically and thus usable outside of Rosetta.


## 1. Inputs and bookkeeping

The caller gives the target for the new skill (which solver + which programming language API), optionally the remaining (time) budget, a potential error from a previous attempt, etc. Run on your own, follow `AGENTS.md`. Start a run with `python -m generation.manage init --run RUN`, and default to one integration, two attempts and 30 minutes. Never start a nested run when called from model-generator.

Before writing any file, record the attempt:

```bash
python -m generation.manage setup-attempt --run RUN --solver ID \
    --skill skills/solver-setup
```

Reuse an existing integration when it already fully supports the target; never relabel another solver to claim the target works. Do not change evaluator or reference acceptance logic or disable isolation. A target that needs a protocol change is a blocker with a proposal. 
Details: [operations](references/operations.md).

## 2. Stand-alone solver skill

Produce one self-contained skill folder `<name>/` that teaches a fresh agent to install the solver or modelling framework and model with it. Below, "solver" covers both solvers and modelling frameworks. The skill to produce is about that tool only; benchmarks, runners and any Rosetta details stay out.

**One skill per solver, one interface file per binding.** The skill is named after the solver alone (`choco`, `pumpkin`, `ortools-cp-sat`; `minizinc`, `clingo` for a tool that is its own language), never after solver and language. Its `SKILL.md` holds what is true of the solver in every binding and a table that routes to `interfaces/<interface>.md`, one file per language binding (`java`, `python`, `cpp`, `rust`; the binding's name, such as `pychoco`, only when one language has two). Examples sit in `assets/<interface>/<example>/`. A skill with one binding has this shape too, so a second binding is added without renaming or moving anything. The layout is in [the template](references/skill-template.md).

**New skill or new interface.** Look for a skill of the same solver API first: one bundle shared by several bindings, or another binding's flat skill (`<solver>-<language>`, the older layout). If one exists, the task is to **add an interface** to it, not to write a second skill: follow [adding an interface](references/merge-interfaces.md), which also turns a flat skill into the shared layout. A different modelling layer over the same backend (JuMP or MiniZinc over HiGHS or Gecode, PuLP over CBC, CPMpy over OR-Tools) is a different API and gets its own skill.

### 2.1 Workflow

| Step | Output |
|---|---|
| 0. Ask the user for the target: solver (+ language) | name/target |
| 1. Search for existing skills, this repository's first | new skill or new interface; each find classified: source / companion / ignore |
| 2. Research, check the licence, install, run a hello-world | `research.md`, working install |
| 3. Write the skill; run `check_assets.py` and `skills-ref` | the skill's skill folder |
| 4. Fresh agent on the toy problems; fix the skill until they pass | test table, `evals/evals.json` |
| 5. Report: path, decision, tested version, test table, related skills, known gaps | `report.md` |

After each step, send the user a one-line progress note: done, next, rough time left. Don't wait for a reply.

**Interface.** Build exactly what the user named; it is one interface of the solver's skill. A modelling framework (JuMP, MiniZinc, CPMpy, Pyomo) uses its default backend unless one is named. A solver gets its **own** API, the one its developers ship (Chuffed → C++, Pumpkin → Rust, Choco → Java/pychoco), unless the user names a combination ("Chuffed via MiniZinc"). With several native interfaces, ask, proposing the one its docs use most. A missing compiler is installed (ask before `sudo`) or reported; it never changes the interface.

**Workspace.** Everything that is not the skill goes in a sibling folder, kept afterwards:

```
<name>-workspace/
  research.md           filled-in references/research.md
  probes/               install and API experiments
  round-N/models/       the test agent's programs, exactly as written
  round-N/results.txt   output of run_toy_tests.py
  report.md
```

### 2.2 Find an existing skill

| Where | How |
|---|---|
| skills.sh registry | `npx skills find <solver>`, also the package name (`pychoco`, `docplex`) |
| A repo's skills | `npx skills add <owner>/<repo> --list` |
| Solver's repo | `skills/`, `.agents/skills/`, `.claude/skills/`, root `SKILL.md`; `gh search code "filename:SKILL.md <solver>"` |
| Python wheel | after installing: `uvx library-skills` |
| Vendor collections | [NVIDIA/skills](https://github.com/NVIDIA/skills), [google/skills](https://github.com/google/skills) |
| Agent-friendly docs | `<docs-site>/llms.txt`, `llms-full.txt`: the best thing to link to |
| Rosetta skills | a skill of the same solver API here means adding an interface to it (see [section 2](#2-stand-alone-solver-skill)); others are for inspiration |

You always write your own skill. Spot-check each find by running one of its examples, then classify it:

| Found skill | Role | What to do |
|---|---|---|
| Overlaps with yours (modelling with this solver) | **Source** | Verify its claims by running them, write your own text, credit it in `sources.md` (URL, version, licence) |
| Covers something else (docs navigation, deployment, tuning) | **Companion** | Recommend it: `metadata.related-skills: "<owner>/<repo>"`, a *Related skill* note under the intro, the install command in the report. Installing is the user's call |
| Stale, broken, or irrelevant | **Ignore** | Say why in the report |

An overlapping skill is a source, never a companion: two skills with the same triggers compete.

### 2.3 Research and install

Fill in [references/research.md](references/research.md) from **official** docs, API reference, examples and changelog. Closed issues ("wrong result", "objective ignored") are the best source of gotchas.

- **Licence**: needing a key, account or registration (full Gurobi, CPLEX, Xpress, Hexaly) → stop and ask. A free edition that installs without one (gurobipy's size-limited licence, CPLEX Community) is fine; put its limits in `compatibility` and *Common issues*.
- Install as the docs recommend, project-local where possible; ask before `sudo` (prevent if possible). Record the tested version in `sources.md`; the skill stays unpinned.
- Done when you have run one tiny model of each kind (satisfy, enumerate all, all optimal, maximise, minimise, infeasible) and one broken on purpose, to see where errors appear.

### 2.4 Write the skill

Start from [references/skill-template.md](references/skill-template.md). Rules:

- **Only what an agent lacks**: exact API names, status semantics, gotchas. No CP/MIP theory.
- **One default per task**, alternatives only when they matter.
- **Tables over prose**, code over tables. Every snippet is run before it goes in.
- **Shared or per interface**: `SKILL.md` states only what holds in every interface (concepts, statuses, search, enumeration strategy). Code, exact API names, install and anything one binding lacks go in its interface file, and a feature that differs between bindings is a row of the interface table. Every claim about a binding is checked in that binding.
- **Examples are runnable files** in `assets/<interface>/<example>/`; only the Quick start lives inline. Check them with `python scripts/check_assets.py <skill-folder> --interface <interface>`; when the solver lives in a container rather than on this machine, add `--image <image>` (and `--env` for what the image needs, such as a binary on `PATH`).
- **Link in place**: each section links its doc page, each table row its API entry.
- **One place per fact**: *Common issues* maps symptom → fix and links back.
- `SKILL.md` and each interface file under ~200 lines; references one level deep.

Validate with [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref), installed from git into a hidden environment:

```bash
uvx --from "git+https://github.com/agentskills/agentskills#subdirectory=skills-ref" skills-ref validate <skill-folder>   # a folder path; `.` fails the name check
```

Without uv, use a venv in `~/.cache/skills-ref/` and `pip install` the same URL.

### 2.5 Test on the toy problems

Seven problems, 18 instances ([README](assets/toy-problems/README.md)).

1. Export what the tester may see, so the answer keys stay out of reach: `python scripts/run_toy_tests.py --export <workspace>/toy`. Spawn a **fresh subagent** given only the new skill, the interface to write in, and `<workspace>/toy`. Task: *one program per problem in `<workspace>/round-N/models/`, taking the instance path as argument, printing solutions as in problem.md; report where the skill was missing, wrong or unclear*.
2. Check every instance:
   ```bash
   python scripts/run_toy_tests.py --public <workspace>/toy --logs <workspace>/round-N/logs \
       --cmd 'python <workspace>/round-N/models/{problem}.py {instance}' | tee <workspace>/round-N/results.txt
   ```
   Adapt `--cmd` to the language; `--problems a,b` reruns a subset. The runner itself runs here, next to the answer keys; when the solver lives in a container, put only the model run in it and mount just the exported copy, at the same path: `--cmd 'docker run --rm --network none -v <workspace>/toy:<workspace>/toy:ro -v <workspace>/round-N/models:/m:ro IMAGE python3 /m/{problem}.py {instance}'`. Each run has 120 s (`--timeout`); a correct but slow paradigm may need more, so raise it and say so in the report. Run the suite in the background, and build compiled models once before it.
3. On failure, the README's table says what the skill lacks. Fix the **skill**, add the test agent's mistake with the solver to its *Common issues*, and rerun with a new fresh agent in `round-N+1/`. Problems, answer keys and checkers stay as they are. A mistake with the toy problems' output convention or file layout is not a skill gap: the test format never enters the skill (no status lines, JSON-per-line output, "declared outputs" or test-machine details). After 3 failed rounds, show the user the failing instances, checker messages and what you tried, and ask whether to continue, accept the gap or stop (unavailable: stop and report).
4. Ship the skill that passed: any later edit needs another round.
5. Write `evals/evals.json` as in the template.

## 3. Rosetta infrastructure

This part adds what Rosetta needs around the skill: `metadata.json`, `Dockerfile`, `run.py`, `readiness_test.py` and a readiness record. How a Rosetta submission (a model written in a solver's interface) must look is the model-generator skill's job, not this one's.

Paths to `generation/`, `evaluation/`, `solvers/` and `skills/` mean repository-root paths. Return **ready** or **blocked** to the caller.

The repository's own tools run on the host, in its Python environment: `.venv/bin/python` (`.venv/Scripts/python.exe` on Windows). A fresh checkout or worktree has none; create it with `python -m venv .venv` and install `requirements.txt` into it. `generation.readiness` needs it, since it runs `readiness_test.py` and the CPMpy reference with that interpreter.

## 3.1 Generate the standalone skill

Follow [section 2](#2-stand-alone-solver-skill):

| add-solver asks | Answer |
|---|---|
| Solver and language | The caller's target |
| Where to write the skill | `solvers/<solver>/skills/<solver>/`; the folder `solvers/<solver>/` holds only `skills/` unless an integration's id is the solver's name. An existing skill of the same solver API stays where it is, and you add an interface to it |
| Integration id | `<solver>_<interface>` |
| Workspace | `generation/runs/RUN/setup/<id>/<attempt>/add-solver-workspace/` |

Two Rosetta rules on top:

- **The solver is never installed on the host.** Write the `Dockerfile` first (step 3), build it,
  and run the probes and toy tests inside the image, e.g.
  `run_toy_tests.py --cmd 'docker run --rm --network none -v "$PWD":/w -w /w --entrypoint python IMAGE <workspace>/round-N/models/{problem}.py {instance}'`.
- **The skill stays standalone.** No DCP-Rosetta, runner or submission instructions in it, and no facts about this integration's container (those go in `solvers/<id>/CONTRACT.md`); it must work outside this repository. Check it three ways:
  `python -m generation.skills validate --project <skill-folder>`, `python -m generation.skills rosetta-mentions skill-folder>` (names), and a [standalone review](references/standalone-review.md) by a fresh agent (meaning). If this setup itself runs as a subagent and cannot start one, return the skill path, and the caller runs the review. Save the clean review's JSON as `solvers/<solver>/standalone-review.json`, next to the skill it reviewed; it covers every interface, so any change to the skill needs a new review.

## 3.2 Add the Rosetta infrastructure

Read the submission contract `solvers/CONTRACT.md` first: it is what every model must do, for any solver, and the runner you build is what lets a model in this solver's own terms do it. Then copy the closest existing integration under `solvers/` (same language, or same way of receiving the instance) and adapt `metadata.json`, `Dockerfile`, `run.py` and `readiness_test.py`. `metadata.json` names the skill and the binding: `"skill": "solvers/<solver>/skills/<solver>"`, `"interface": "<interface>"`.

Write the integration contract `solvers/<id>/CONTRACT.md`: how this runner realises the submission contract, under the headings of its *Mapping checklist*, with the pilot fixture as its example. Every claim in it must be true of your `run.py`. It is what the model-generator skill reads to write a model for this integration, next to the standalone skill, so the standalone skill itself stays free of it.

The rules for each file, and the choice of who converts the JSON instance, are in [integration files](references/integration.md). Check them as you go:

```bash
python <this-skill>/scripts/check_integration.py ID --static
```

Build with `python -m evaluation.build <id>`, bounded by the remaining budget. Evaluation never builds or installs implicitly.

## 3.3 Readiness

```bash
python -m generation.readiness check --solver ID --output solvers/ID/readiness.json
```

This runs `solvers/<id>/readiness_test.py` against the built image and records the result only when every required check passes. Set `"readiness_level": 2` in `metadata.json`, which adds the bug-class checks of [integration files](references/integration.md); besides the required checks, include one that a solver crash comes back as `error` with the solver's own message. Tests skipped because Docker or the image is missing do not count. The record is write-once: after a fix,
rebuild, delete `readiness.json`, and check and verify again (on a separately tagged image while a campaign is still evaluating on `:v1`). Then register it as a pilot (see *Once certified* in [integration files](references/integration.md)) and run `scripts/check_integration.py ID` without `--static`: it must exit 0 before you return **ready**. After changing shared runner code, rerun the affected existing integrations too.

## 3.4. Return

Write the evidence under `generation/runs/RUN/setup/<id>/`: changed files, sources, versions, commands and their output, image identity, capabilities and limitations, and add-solver's report with its toy-test table. Record `setup_finished` or `setup_blocked` with `generation.manage event`.

Return **ready** only after readiness passed. Otherwise return **blocked** with the exact failure, the attempts spent and what is left. Stop when the budget is spent; never recurse.


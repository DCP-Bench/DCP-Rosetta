# Setup: `hexaly_python`

Hexaly Optimizer 15.0 (formerly LocalSolver) from its native Python API, `hexaly`. A
commercial solver that needs a licence file for every run; this setup uses an academic
licence (1 concurrent use, Hexaly up to 16.0, no hardware signature, expires 2027-01-31).

## Files created or changed

| Path | What it is |
| --- | --- |
| `solvers/hexaly/skills/dcp-hexaly/` | the standalone skill: `SKILL.md`, `interfaces/python.md`, eight examples, sources, evals |
| `solvers/hexaly/standalone-review.json` | the clean standalone review |
| `solvers/hexaly/python/run.py` | the runner: proof semantics, soft no-good enumeration, output reading |
| `solvers/hexaly/python/Dockerfile` | `python:3.12.11-slim-bookworm`, the locked `hexaly` wheel, the licence as an optional build secret |
| `solvers/hexaly/python/requirements.txt` | `hexaly==15.0.20261026`, hashed by `evaluation.lock` |
| `solvers/hexaly/python/metadata.json`, `CONTRACT.md` | integration metadata and the modeller's contract |
| `solvers/hexaly/python/readiness_test.py`, `readiness.json`, `readiness/` | 27 checks and their record |
| `evaluation/build.py` | passes a Dockerfile's build secrets from `DCP_SECRET_<ID>`; never with `--gha-cache` |
| `tests/test_solvers.py`, `tests/fixtures/model_hexaly.py` | pilot registration; container cases skip without the secret |
| `README.md`, `.gitignore` | the integration named; `license.dat` ignored |

`runner/runtime.py` and the evaluator's acceptance logic are unchanged.

## Versions

- Base image `python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7`.
- `hexaly==15.0.20261026` (wheel sha256 `33a97cf4555c0591ee3678630d6cd5e2b6333a7839485a38e25a2022a011374b`).
- Image `dcp-eval/hexaly_python:v1`, id `sha256:d62f84da0da16e76176687e9091ff041ca39b2f6bcabb7c4109a3725dd53ea91`,
  recipe `sha256:89ad96c323de3ed65876e56970d669bd777c877e1f9d58cda150ea940909ecb7`.

## The licence

The container has no network, so the licence must be inside the image. It enters as the
BuildKit secret `hexaly_license` (`DCP_SECRET_HEXALY_LICENSE` names the file on the
building machine) and is installed at `/opt/hexaly_15_0/license.dat`, mode 0444. It is in no
repository file; a scan of every new file for the licence key found nothing. Consequences:

- The image holds the licence and must stay on the machine that built it.
- CI has no secret: it builds a licence-free image, and `test_pilots` / `test_maximization`
  skip `hexaly_python` with "needs build secrets: DCP_SECRET_HEXALY_LICENSE" (checked).
- BuildKit reuses a cached licence layer for a later build without the secret on the same
  machine; a remote cache never receives it because `build.py` drops secrets under `--gha-cache`.
- The submission runs as the same user as the runner, so a submission can read the file.
- The licence's 1-concurrent-use term is not enforced offline (three containers solved at
  once); runs are kept serial by hand.

## Design decisions

- **Entry point** `build(instance) -> (HexalyOptimizer, outputs)`; the runner configures,
  closes and solves. A `with` block in the submission deletes the optimizer, and the run
  fails with "Cannot call this method on an object that is no longer valid" (readiness
  check `with_block`).
- **Proof semantics.** `gap_limit` 0 (the default 1e-4 reported OPTIMAL with the bound 1203
  above the objective); only `OPTIMAL` is reported; `FEASIBLE` and `INFEASIBLE` are
  `timeout`; only `INCONSISTENT` is `unsat`.
- **Four threads.** Hexaly's bounds run beside the search: ft06 stayed at bound 54 for 30 s
  with 1 or 2 threads and was proven in 0.4 s with 4, on one CPU (check `bound_threads`).
- **Soft no-goods.** Hard no-goods never prove exhaustion; minimising the number of
  repeated reported solutions does (checks `exhausted_enumeration`, `optimal_enumeration`,
  pilot 7/7).
- **Typing only on a closed model.** Hexaly answers `is_int` and the like only when the
  model is closed; the first dry run failed 11 checks on this, fixed by classifying outputs
  before reopening.

## Evidence

- Probes `add-solver-workspace/probes/p01..p24` and `research.md`.
- Readiness dry runs `evidence/readiness-dryrun-1.json` (11 failures, typing bug) and
  `-2.json` (27/27); the record `solvers/hexaly/python/readiness.json` with its evidence.
- `check_integration.py hexaly_python`: 46 passed, 0 warnings, 0 failed.
- Skill examples: `check_assets.py --interface python --image hexaly-probe:dev`, 8/8.
- `skills-ref validate` was not run: the session's permission classifier refused to run it
  from git. `generation.skills validate --project` and `rosetta-mentions` pass.

## Toy tests (fresh agent, skill only)

| Round | Skill state | Result | Gaps reported and fixed |
| --- | --- | --- | --- |
| 1 | first draft | 18/18 | enumeration formulation, zero-solution enumeration, resetting parameters between solves |
| 2 | after round 1 | 18/18 | final proof dominates enumeration, no-good width, violation forms for inequalities and equations, chained comparison, `distinct` needs an array |
| 3 | after round 2 | 18/18 | one soft solve both finds solutions and proves infeasibility, presolve misses some cryptarithms, when the short no-good is wrong, `partition`/`disjoint`/`cover` calls, violation calls per binding |
| 4 | after round 3 (shipped) | 18/18 | none acted on; known gaps below |

Known gaps in the shipped skill, reported by round 4 and not verified or changed (any edit
would need a fifth round): when Hexaly calls a Python function passed to `lambda_function`
(the examples rebind loop variables, and results show no late-binding bug); whether
`interval(lo, hi)` caps the end or the start; `model.list(1)` and `model.and_` with zero or
one argument; where diagonal constraints go in the posting-order observation; more than 10
letters in a cryptarithm (pigeonhole under hard constraints). `skills-ref` was not run.

Five standalone reviews ran, each by a fresh agent given only the skill and the rubric. None
found a harness leak. Reviews 1 to 4 found inconsistencies between `SKILL.md`, the interface
page and the examples, fixed after each; review 5, on the shipped text, found none
(`solvers/hexaly/standalone-review.json`).

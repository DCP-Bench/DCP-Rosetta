# Integration files

What an integration folder `<integration>/` holds besides the standalone skill (`solvers/<solver>/<interface>/` beside the solver's skill), in build order. Full protocol: `evaluation/README.md`; readiness: `generation/AGENTS.md`; enforced rules: `tests/test_solvers.py`.

## Contents

1. [Who converts the instance](#1-who-converts-the-instance): decide this first
2. [`Dockerfile`](#2-dockerfile)
3. [`run.py`](#3-runpy)
4. [`metadata.json`](#4-metadatajson)
5. [`CONTRACT.md`](#5-contractmd)
6. [`readiness_test.py`](#6-readiness_testpy)
7. [Once certified](#7-once-certified)

Check the files as you go (PASS/WARN/FAIL per rule, exit 1 on failure; behaviour is
left to `readiness_test.py`):

```bash
python <this-skill>/scripts/check_integration.py ID --static   # while building; no Docker needed
python <this-skill>/scripts/check_integration.py ID            # at the end; also verifies readiness.json
```

## 1. Who converts the instance

Every model for this integration inherits this choice, so pick the pattern closest to how the standalone skill already models:

| Pattern | Who converts | Used by |
| --- | --- | --- |
| The model reads the dict | the submission, via `instance["n"]` | `cpmpy_python`, `ortools_cp_sat_python`, `z3_python` |
| The framework binds it | `run.py`, feeding each JSON key to the framework's data API | `minizinc_gecode` |
| A harness parses it | code baked into the image hands the parsed object to a fixed entrypoint | `ortools_cp_sat_cpp` |

When the input is generated source (facts for an ASP grounder, a bespoke data file), either the submission or `run.py` emits it; that choice is the contract for every model. Conversion happens inside the container, and only one submission file is staged: shared conversion code goes in the image or `run.py`, and a design needing more files is unsupported (report it).

`instance_binding` in `metadata.json` says what the runner can bind, so `generation.next_work` withholds only the pairs it never could:

| Value | Use when | What happens |
| --- | --- | --- |
| omitted (`"any"`) | the submission reads the instance itself | nothing is withheld |
| `"rectangular_uniform"` | the data interface takes only rectangular arrays of one type | pairs with ragged or mixed-type fields are withheld |
| `"reshaped"` | `run.py` reshapes fields itself (padding, splitting) | `run.py` defines `refusal(name, value)` to say what it cannot bind; see `essence_prime_minion`, `idp_z3` |

`generation.brief` imports `refusal()` on the host, so it must not import the solver or
write to stdout. It covers reshaping only; a string field is refused at run time, when
the model declares it. Do not use the brief's generic `unbindable_fields` instead: it is
not per integration and was wrong for several runners.

When the framework binds the data (a typed modelling language):

- **Bind only the fields the model declares.** Instances carry strings (`name`, `note`)
  and data a given model may not use; binding every key fails those instances.
- **Offer derived sizes.** Finite index sets cannot change size between instances, so let
  the model declare optional sizes per field (`F_dim1`, `F_dim2`), pad ragged lists and
  offer their lengths (`F_len`), and split mixed-type rows into one field per column.
- **Escape reserved words.** For a field or output named like a keyword (`matrix`, `E`),
  let the model write `name_`, and map it back on input and output.

## 2. `Dockerfile`

- Pin the base image by digest and every dependency by version.
- It runs unprivileged, read-only, without network, with bounded scratch space;
  compilation happens inside it, within its own budget.
- Check `.dockerignore` before relying on a build file; never widen the context to
  datasets, references, credentials or models.
- The final `ENTRYPOINT` runs the intended runner.

## 3. `run.py`

The protocol is in `evaluation/README.md`. In short:

- Read `/input/model.<ext>` and `/input/request.json`; write JSONL `solution` records
  with `values`, then exactly one `status`; log to stderr. Reuse `runner/runtime.py`.
- Return explicit `unsupported`, `error` and `compilation_error` statuses.
- Never invent solutions, alter the submission or emit more solutions than requested;
  fewer only with `complete` (search exhausted).

Each rule below fixes a bug a campaign found; the readiness check that catches it is in
brackets ([section 6](#6-readiness_testpy)).

- **Prove the optimum before emitting** (`optimization_timeout`). Know whether there is an
  objective before solving, so every kill, crash and deadline path does too. On a timeout
  before the proof, emit no solutions, only `timeout`: the evaluator checks solutions
  first, so an unproven incumbent is rejected as suboptimal, not inconclusive.
- **Parenthesise a re-posted objective** (`optimum_enumeration`). To enumerate at the
  optimum, post `(objective) = optimum`; where a sum or quantifier extends as far right as
  possible, the appended text is otherwise swallowed.
- **Check that a strict-bound call is strict** (`minimization_step_one`). When the runner
  bounds the objective itself, confirm from the docs and a test whether "better than the
  bound" is strict; an off-by-one skips the optimum.
- **Count distinct declared outputs** (`auxiliary_free_distinct`). A free auxiliary
  variable makes the solver repeat outputs; deduplicate on the declared outputs and
  re-solve with a nogood per assignment until the count is reached or search is exhausted.
- **Use the solver's own solution checker if it has one.** ACE accepted wrong tuples for a
  product of four or more variables; reject such a solution and keep searching.
- **Report a failure, never a timeout** (`error_detail`). A crash, out-of-memory,
  reserved-identifier or compile error returns `error` or `compilation_error` with the
  tool's own message. Find where the solver hides it (a log file, stdout, a verbose flag)
  and forward it; without it, modelling agents cannot fix their model.
- **Send the solver's stdout to stderr** (`stray_stdout`); the protocol owns stdout.

## 4. `metadata.json`

Copy an existing `solvers/*/metadata.json` (JSON) and use only the keys below:
readiness, evaluation and the website read them.

```json
{
  "id": "framework_language",
  "name": "CPMpy (Python)",
  "language": "python",
  "framework": "cpmpy",
  "solver": "ortools",
  "paradigms": ["cp"],
  "image": "dcp-eval/framework_language:v1",
  "extension": ".py",
  "enumeration": true,
  "readiness_level": 2,
  "protocol_version": 1
}
```

| Key | Rule |
| --- | --- |
| `id` | Required. Lowercase letters, digits and underscores; unique and stable. Skill names use hyphens instead. |
| `image` | Required. `dcp-eval/<id>:v1`. |
| `extension` | Required. The submission's file extension. A new one needs an `EXTENSION_LANGUAGE` entry in `generate_site.py`. |
| `enumeration` | Required. Literal Boolean. |
| `optimization` | Add `false` only when the integration genuinely cannot optimise. |
| `compilation` | Add `true` only when submissions are compiled. |
| `readiness_level` | `2` for every new integration; it adds the bug-class checks. Existing integrations without the key are at level 1 until upgraded. |
| `instance_binding` | See [section 1](#1-who-converts-the-instance). |
| `name` | What the website shows (it never shows `id`). See the naming rules below. |
| `framework` | The package name (`cpmpy`, `docplex`, `pychoco`). |
| `solver` | The backend. Needs a display label in `BACKEND_NAMES` in `generate_site.py`, unless `name` already contains it. |
| `language` | What a submission is written in; sets the website's label and syntax highlighting. A new value needs a row in `LANGUAGES` in `generate_site.py` (use `plaintext` when highlight.js has no grammar for it). |
| `paradigms` | Required. IDs from `solvers/paradigms.json` for the paradigm a **submission is written in**, not the backend's technology: CP-SAT is `["cp"]`. Several tags when a submission really belongs to several (`swipl_clpfd` is `["cp", "clp"]`). A new tag goes into `solvers/paradigms.json` in the same commit. |
| `protocol_version` | `1`. |

`optimization`, `compilation` and `enumeration` select the required readiness checks:
never declare an untested capability.

**Naming** (enforced by `tests/test_solvers.py` and `tests/test_site.py`; renaming is
cheap, since `name` is not in the readiness record):

- A library that drives one solver is named after the solver, with the host language in
  brackets: `CPLEX (Python)`, `Choco (Python)`, `OR-Tools CP-SAT (C++)`.
- A modelling layer over several solvers is named after the layer: `CPMpy (Python)`,
  `PuLP (Python)`, `JuMP (Julia)`.
- A system with its own language stands alone: `MiniZinc`, `Picat`, `clingo`,
  `SWI-Prolog`. When the language and the system that runs it have different names, the
  language is the `name` and the system goes in `solver`.
- Brackets hold only the host language. Neither the paradigm nor the backend goes in the
  name; the website prints the backend beside it (`MiniZinc · Gecode`).
- Names are distinct.

## 5. `CONTRACT.md`

Tells modellers how this runner realises `solvers/CONTRACT.md`. The model-generator
reads it beside the standalone skill; a model attempt refuses an integration without it.

- Use exactly the headings of the *Mapping checklist* in `solvers/CONTRACT.md`:
  `## Submission file`, `## Entrypoint`, `## Instance`, `## Outputs`, `## Objective`,
  `## Solving`, `## Compilation`, `## Environment`, `## Traps`, `## Example`. Follow
  `solvers/cpmpy/python/CONTRACT.md` as a model.
- State what `run.py` does, not what you meant it to do: signatures, how the instance is
  represented, the output container, the objective form, the settings the runner forces.
- Every fact about the container (binary paths, environment variables, network,
  preinstalled packages) goes under `## Environment`, never into the standalone skill.
- `## Example` is the pilot fixture (see [section 7](#7-once-certified)).
- Leave out what `solvers/CONTRACT.md` already says and what the standalone skill teaches
  about the solver's API.

## 6. `readiness_test.py`

Adapt `solvers/cpmpy/python/readiness_test.py`, which implements every check below with
a trusted reference. It drives the real evaluator against the built image, prints a JSON
object of check name to Boolean, and exits nonzero on any failure. Each check must be
able to fail, with its submission in this integration's own form.

**Required at every level:** `satisfaction`, `changed_instances`, `malformed_output`,
`empty_output`, `timeout_cleanup`, `isolation`, `missing_image`; `minimization` and
`maximization` (or `unsupported_optimization`); `enumeration` (or
`unsupported_enumeration`); `compilation_error` when compiled.

**Added at `readiness_level: 2`**, because tiny `x + y` models never reach the runner
bugs real models hit:

| Check | Required when | Bug class | The submission, and what must happen |
| --- | --- | --- | --- |
| `output_shapes` | always | outputs the runner cannot carry | a three-level integer array, a Boolean matrix and a value beyond 32 bits: accepted, or `unsupported` with the limit documented under `## Outputs` |
| `instance_shapes` | always | instance binding | ragged rows, rows of mixed types, an unused string field and `name`/`note`, on two instances of different shapes: accepted (for `rectangular_uniform`, the refusal the contract documents) |
| `error_detail` | always | errors hidden as timeouts or bare exit codes | a submission that makes the solver or its library raise: `execution_error` with that tool's own message in the detail |
| `stray_stdout` | always | output corrupting the protocol | a submission that prints: accepted |
| `large_model` | always | stack and recursion limits | a sum over 3000 Booleans, used as an output: accepted within 120 s |
| `optimization_timeout` | it optimises | an unproven optimum emitted when time runs out | an easy reference; the submission adds an unrelated hard part to its objective (a Golomb ruler), so a solution comes fast but cannot be proven within a 3 s budget: `execution_timeout` with **zero solutions received** |
| `minimization_step_one` | it optimises | an off-by-one bound in a runner that bounds the objective itself | a minimisation whose first solution is exactly optimum + 1 (steer the search there if the runner does branch and bound): accepted |
| `auxiliary_free_distinct` | it enumerates | duplicate outputs from free auxiliaries | a free auxiliary variable outside the outputs, `solution_limit=3`: accepted with 3 distinct solutions |
| `optimum_enumeration` | it optimises and enumerates | a re-posted objective parsed or pinned wrongly | a compound objective (a sum) with ten optima, `solution_limit=3`: accepted with 3 solutions checked |

Full list: *Integration readiness* in `generation/AGENTS.md`.

## 7. Once certified

**Register the pilot**, which `tests/test_solvers.py` requires of every integration with
a `readiness.json`: add it to `PILOTS` with a fixture model under `tests/fixtures/`;
unless it cannot optimise, add it to `MAXIMIZATION_SWAPS` with the fixture's
minimise/maximise spelling; and name it by its `name` in `README.md`.

**Re-certify after a change.** The record binds the image identity, the hashes of
`run.py`, `Dockerfile` and `readiness_test.py`, and every `metadata.json` field except
`name` and `paradigms`. Changing any of them, or rebuilding the image (image IDs are not
reproducible), invalidates it. The record is write-once:

1. Rebuild. While models are evaluated on `:v1`, test the fix on a separately tagged
   image and rebuild `:v1` only once nothing runs on it.
2. Delete `readiness.json`.
3. Run `generation.readiness check`, then `verify`.

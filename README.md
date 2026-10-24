# DCP Rosetta

[![Website](https://img.shields.io/badge/Website-DCP%20Rosetta-4f46e5?logo=googlechrome&logoColor=white)](https://dcp-bench.github.io/DCP-Rosetta/)
[![Deploy](https://github.com/DCP-Bench/DCP-Rosetta/actions/workflows/deploy.yml/badge.svg)](https://github.com/DCP-Bench/DCP-Rosetta/actions/workflows/deploy.yml)
[![License](https://img.shields.io/github/license/DCP-Bench/DCP-Rosetta)](LICENSE)

DCP Rosetta collects executable models of the [DCP-Bench Open](https://github.com/DCP-Bench/DCP-Bench-Open) problems, written in many modelling frameworks and solved by many solvers. It holds the evaluator that accepts or rejects each model, the solver integrations the evaluator runs, the agent skills that write the models, and the catalogue website. The problems live in that repository, checked out here as the `bench/` submodule.

[**Open the interactive catalogue →**](https://dcp-bench.github.io/DCP-Rosetta/)

The generated models shown on the website are a draft collection: every one was
accepted by this repository's evaluator, but coverage is still growing, so the
collection is not yet a settled generated-model benchmark. When reporting
results, cite the DCP Rosetta commit you used; it also pins the version of the
problems in `bench/`.

## Getting started

```bash
git clone --recurse-submodules https://github.com/DCP-Bench/DCP-Rosetta.git
```

You need Python 3.12 and the libraries in `requirements.txt`, which also cover
the dataset tooling in `bench/`. Evaluating a model needs a running Docker Linux
engine.

On Windows, keep the checkout in a short folder such as `C:\code\DCP-Rosetta`:
the longest tracked path is 184 characters, and Windows limits a full path to
260 unless long paths are enabled for both Git (`core.longpaths`) and the
system.

`bench/` is pinned to one commit of the problems. To move to their latest
`main`, run `git submodule update --remote bench` and commit the new pointer.

## The catalogue website

From the repository root, build the static site and serve it:

```bash
(cd bench && python jsonl_convert.py)
python generate_site.py
python -m http.server 8000 --directory site
```

Then open <http://localhost:8000/>. The hosted version is the [interactive catalogue](https://dcp-bench.github.io/DCP-Rosetta/).

Alongside the problem catalogue, the
[solver breakdown](https://dcp-bench.github.io/DCP-Rosetta/paradigms.html)
groups the verified models by the kind of model they are — constraint
programming, CLP, MIP, SMT, ASP and so on — with the solvers behind each kind,
how much of the catalogue each one reaches, and which problems have been
modelled in more than one of them. Those are the problems worth reading side by
side.

## Repository Structure

The models and the catalogue:

| Path | What it holds |
| --- | --- |
| `bench/` | The problems, as a git submodule: per problem a CPMpy reference with its description, and its instances. Changes to it go to that repository. |
| `generated_models/` | Models produced by generative systems, with the verdict each one received. Not ground truth. |
| `web/` | Source for the catalogue website. `generate_site.py` builds it into `site/`, which is generated and not committed. |

The evaluation framework:

| Path | What it holds |
| --- | --- |
| `evaluation/` | The verifier. Runs a candidate in a container and checks its answers against the reference model. See [evaluation/README.md](evaluation/README.md). |
| `solvers/` | One directory per framework integration: image, runner, readiness checks, and the modelling skill for that framework. Each one declares the modelling paradigm its submissions are written in, drawn from the vocabulary in [solvers/paradigms.json](solvers/paradigms.json). |
| `runner/` | The protocol that runs inside those images. |
| `tests/` | Unit tests, plus container tests behind `DCP_CONTAINER_TESTS=1`. |

The model generation framework. *Rosetta* names the collection of models (one per problem
and framework, shown side by side in the catalogue) and the machinery here that writes and
checks them: integrations, contracts, evaluator and campaign harness. A Rosetta-independent
skill works outside this repository; a skill in `rosetta-skills/` works only inside it.

| Path | What it holds |
| --- | --- |
| `skills/` | Public, Rosetta-independent skills: `add-solver` writes a standalone skill for any solver. |
| `rosetta-skills/` | Instructions an agent follows here: `model-generator` runs a "campaign", `solver-setup` adds a framework (on top of `add-solver`), `instance-curator` adds instances to the problems in `bench/`. |
| `generation/` | The campaign harness — work queue, run ledger, readiness gate — and `runs/`, the record of past campaigns. See [generation/README.md](generation/README.md); its agent-facing contract is [generation/AGENTS.md](generation/AGENTS.md). |


## Evaluation framework

The container-based [evaluation package](evaluation/README.md) provides a Python API, a JSON CLI and configurable instance/solution counts. The certified integrations are CPMpy (Python), OR-Tools CP-SAT (Python), OR-Tools CP-SAT (C++), Chuffed (C++), Gecode (C++), HiGHS (C++), MiniZinc, Z3 (Python), cvc5 (Python), clingo, SWI-Prolog, PuLP (Python), Python-MIP (Python), Choco (Python), Choco (Java), MaxiCP (Java), JaCoP (Java), PyCSP3 (Python), Pumpkin (Rust), Huub (Rust), PySAT (Python), Paramita (Python), hermax (Python), Exact (Python), Gurobi (Python), CPLEX (Python), SCIP (Python), Picat, ECLiPSe, JuMP (Julia), Essence' and FO(·), named here as the catalogue names them. Build their images explicitly with `python -m evaluation.build`. That is all the evaluator needs; the model-generation workflow additionally wants `python -m generation.readiness check` once per integration after a build, because a readiness record is tied to the exact image it was checked against.

A model is accepted by falsification rather than by comparison: the evaluator enumerates the candidate's solutions and looks for one the reference rejects. Finding none within the budget is what acceptance means, so a larger solution limit is a stronger test.

### Checking a file of models

`eval.py` checks every model in a JSONL file against the example instance of its problem:

```bash
python eval.py --dataset_file bench/dcp-bench-open.jsonl --test_file sample_test.jsonl --modelling_framework CPMpy
```

`--dataset_file` is the jsonl that `jsonl_convert.py` builds inside `bench/`, `--test_file` holds the models, and `--modelling_framework` names a registered container integration. Legacy aliases are `CPMpy`, `OR-Tools`/`ortools`, and `MiniZinc`; unsupported frameworks fail explicitly.

Each line of the test file is a JSON object with two keys: `id`, the problem ID (e.g. `csplib_001_car_sequencing`), and `model`, the model as runnable code. A model must print its solution as JSON whose keys are the problem's declared outputs; unexpected keys or value types count as wrong.

[sample_test.jsonl](sample_test.jsonl) holds 5 models, four of them wrong on purpose, so running it shows what each kind of rejection looks like:

```
FAIL csplib_001_car_sequencing   execution_error  TypeError: list indices must be integers or slices, not _IntVarImpl
FAIL csplib_002_template_design  execution_error  IndexError: index 7 is out of bounds for axis 0 with size 7
FAIL csplib_005_autocorrelation  invalid_output  Expected exactly these outputs: ['sequence']
FAIL csplib_006_golomb_rulers    suboptimal_solution  Declared outputs cannot achieve the reference optimum
PASS csplib_007_all_interval     accepted

1/5 accepted. Full JSON in summary.txt.
```

To check a model against the other instances of a problem, use the evaluation package directly; see [evaluation/README.md](evaluation/README.md).

## Generating models

The same problem modelled in many frameworks is more useful than the same
problem modelled once, so this repository also contains the machinery to write and evaluate models.

An agent follows `rosetta-skills/model-generator`: it picks work from a queue ordered
so that problems with several instances come first (a model that hardcoded the
example cannot survive a second instance), writes a model from the reference,
and submits it to the evaluator. A model is kept only when the evaluator
accepts it.

Every campaign leaves a ledger under `generation/runs/`: what was attempted,
what the evaluator said, and what was kept, including the attempts that failed.

## How to Contribute

A new solver integration follows `rosetta-skills/solver-setup`, and new models follow
`rosetta-skills/model-generator`. New problems and instances belong in the problem
repository linked above.

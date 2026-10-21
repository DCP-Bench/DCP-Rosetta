# DCP Rosetta

[![Website](https://img.shields.io/badge/Website-DCP%20Rosetta-4f46e5?logo=googlechrome&logoColor=white)](https://dcp-bench.github.io/DCP-Rosetta/)
[![Deploy](https://github.com/DCP-Bench/DCP-Rosetta/actions/workflows/deploy.yml/badge.svg)](https://github.com/DCP-Bench/DCP-Rosetta/actions/workflows/deploy.yml)
[![Paper](https://img.shields.io/badge/Paper-arXiv%3A2506.06052-b31b1b?logo=arxiv&logoColor=white)](https://arxiv.org/abs/2506.06052)
[![License](https://img.shields.io/github/license/DCP-Bench/DCP-Rosetta)](LICENSE)

DCP Rosetta collects executable models of the [DCP-Bench Open](https://github.com/DCP-Bench/DCP-Bench-Open) problems, written in many modelling frameworks and solved by many solvers. It holds the evaluator that accepts or rejects each model, the solver integrations the evaluator runs, the agent skills that write the models, and the catalogue website. The problems themselves live in DCP-Bench Open, checked out here as the `bench/` submodule.

[**Open the interactive catalogue →**](https://dcp-bench.github.io/DCP-Rosetta/)

The generated models shown on the website are a draft collection: every one was
accepted by this repository's evaluator, but coverage is still growing, so the
collection is not yet a settled generated-model benchmark. When reporting
results, cite the DCP Rosetta commit you used; it pins the DCP-Bench Open commit
through `bench/`.

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

`bench/` is pinned to one DCP-Bench Open commit. To move to its latest `main`,
run `git submodule update --remote bench` and commit the new pointer.

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
| `bench/` | DCP-Bench Open as a git submodule: the problems, their instances and `SOURCES.md`. Changes to it go to that repository. |
| `generated_models/` | Models produced by generative systems, with the verdict each one received. Not ground truth. |
| `web/` | Source for the catalogue website. `generate_site.py` builds it into `site/`, which is generated and not committed. |

The evaluation framework:

| Path | What it holds |
| --- | --- |
| `evaluation/` | The verifier. Runs a candidate in a container and checks its answers against the reference model. See [evaluation/README.md](evaluation/README.md). |
| `solvers/` | One directory per framework integration: image, runner, readiness checks, and the modelling skill for that framework. Each one declares the modelling paradigm its submissions are written in, drawn from the vocabulary in [solvers/paradigms.json](solvers/paradigms.json). |
| `runner/` | The protocol that runs inside those images. |
| `tests/` | Unit tests, plus container tests behind `DCP_CONTAINER_TESTS=1`. |

The model generation framework:

| Path | What it holds |
| --- | --- |
| `skills/` | Instructions an agent follows: `model-generator` runs a "campaign", `solver-setup` adds a framework, `instance-curator` adds instances to the problems in `bench/`. |
| `generation/` | The campaign harness — work queue, run ledger, readiness gate — and `runs/`, the record of past campaigns. See [generation/README.md](generation/README.md); its agent-facing contract is [generation/AGENTS.md](generation/AGENTS.md). |


## Evaluation framework

The container-based [evaluation package](evaluation/README.md) provides a Python API, a JSON CLI and configurable instance/solution counts. The certified integrations are CPMpy (Python), OR-Tools CP-SAT (Python), OR-Tools CP-SAT (C++), Chuffed (C++), Gecode (C++), MiniZinc, Z3 (Python), clingo, SWI-Prolog, PuLP (Python), Choco (Python), Choco (Java), PyCSP3 (Python), Pumpkin (Rust), PySAT (Python), Paramita (Python), hermax (Python), Exact (Python), Gurobi (Python), CPLEX (Python), SCIP (Python), Picat, JuMP (Julia), Essence' and FO(·), named here as the catalogue names them. Build their images explicitly with `python -m evaluation.build`. That is all the evaluator needs; the model-generation workflow additionally wants `python -m generation.readiness check` once per integration after a build, because a readiness record is tied to the exact image it was checked against.

A model is accepted by falsification rather than by comparison: the evaluator enumerates the candidate's solutions and looks for one the reference rejects. Finding none within the budget is what acceptance means, so a larger solution limit is a stronger test.

### Automated evaluation of solution accuracy

The `eval.py` script can be used to automate this evaluation process provided that there exists a file containing the generated models. For example, if you have the file `sample_test.jsonl` with generated models, you can run:

```bash
 python eval.py --dataset_file bench/dcp-bench-open.jsonl --test_file sample_test.jsonl --modelling_framework CPMpy
```

Here, `--dataset_file` specifies the path to the jsonl version of the benchmark (built by `jsonl_convert.py` in `bench/`, or downloaded from a [DCP-Bench Open release](https://github.com/DCP-Bench/DCP-Bench-Open/releases)), `--test_file` specifies the path to the file with generated models, and `--modelling_framework` indicates a registered container integration. Legacy aliases are `CPMpy`, `OR-Tools`/`ortools`, and `MiniZinc`; unsupported frameworks fail explicitly.

### Creating your test file with models to be evaluated

Regarding the test file, each line should be a JSON object with two keys: `id` and `model`.
* `id`: The ID of the problem exactly as it appears in the dataset (e.g., `csplib_001_car_sequencing`).
* `model`: The generated model for the problem (as a string representing runnable code). Make sure that it eventually outputs the solution as a json with key(s) as described in the `decision_variables` entry and values as would be expected in the problem. This is part of the evaluation as well: unexpected keys, or value types are considered incorrect. This is because our automatic evaluation is based on the solution printed by the submitted models.

An example test file with 5 generated models is included ([sample_test.jsonl](sample_test.jsonl)). Four of them are wrong on purpose, so running it shows what each kind of rejection looks like:

```
FAIL csplib_001_car_sequencing   execution_error  TypeError: list indices must be integers or slices, not _IntVarImpl
FAIL csplib_002_template_design  execution_error  IndexError: index 7 is out of bounds for axis 0 with size 7
FAIL csplib_005_autocorrelation  invalid_output  Expected exactly these outputs: ['sequence']
FAIL csplib_006_golomb_rulers    suboptimal_solution  Declared outputs cannot achieve the reference optimum
PASS csplib_007_all_interval     accepted

1/5 accepted. Full JSON in summary.txt.
```

`eval.py` checks the embedded example instance only. To check a model against the other instances of a problem, use the evaluation package directly — see [evaluation/README.md](evaluation/README.md).

## Generating models

The same problem modelled in many frameworks is more useful than the same
problem modelled once, so this repository also contains the machinery to write and evaluate models.

An agent follows `skills/model-generator`: it picks work from a queue ordered
so that problems with several instances come first (a model that hardcoded the
example cannot survive a second instance), writes a model from the reference,
and submits it to the evaluator. A model is kept only when the evaluator
accepts it.

Every campaign leaves a ledger under `generation/runs/`: what was attempted,
what the evaluator said, and what was kept, including the attempts that failed.

## How to Contribute

New problems and new instances for existing problems go to
[DCP-Bench Open](https://github.com/DCP-Bench/DCP-Bench-Open); its
[Contributing Guide](https://github.com/DCP-Bench/DCP-Bench-Open/blob/main/CONTRIBUTING.md)
has the format. A new solver integration follows `skills/solver-setup`, and new
models follow `skills/model-generator`.

## Citation

Feel free to cite our work as follows:

```bibtex
@misc{michailidis2026dcpbenchopenevaluatingllmsconstraint,
      title={DCP-Bench-Open: Evaluating LLMs for Constraint Modelling of Discrete Combinatorial Problems}, 
      author={Kostis Michailidis and Dimos Tsouros and Tias Guns},
      year={2026},
      eprint={2506.06052},
      archivePrefix={arXiv},
      primaryClass={cs.AI},
      url={https://arxiv.org/abs/2506.06052}, 
}
```

```bibtex
@dataset{dcpbenchopen,
  author       = {Michailidis, K. and Tsouros, D. and Guns, T.},
  title        = {DCP-Bench-Open},
  year         = {2025},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.17800138},
  url          = {https://doi.org/10.5281/zenodo.17800138}
}
```

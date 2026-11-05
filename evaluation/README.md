# Model evaluation

Runs a submitted model inside a locked-down container and checks its declared
outputs against a CPMpy reference whose optimum has been proven independently.

## What acceptance means

Evaluation looks for a **counterexample**: a solution of the submitted model
that the reference does not accept. `solution_limit` is the budget for that
search, not a requirement — a higher limit is a stronger test, never a stricter
pass bar. Exhausting the submitted model before reaching the limit is a pass.

`accepted=true` therefore means no counterexample was found within budget,
against the reference's **declared outputs** — not that the model is equivalent
to the reference. An overconstrained model can pass, because being too strict
leaves no trace in the outputs examined; a submission with no solutions at all
is the one exception and always fails. Some references declare only an
objective value. Reference UNSAT is unsupported in v1.

`tolerate_inconclusive` relaxes coverage without relaxing soundness: an instance
that only times out (`reference_timeout` or `execution_timeout`) or runs out
of memory (`memory_limit`) is recorded in
`skipped_instances` and the remaining instances are still checked, and
acceptance then needs at least one instance verified — `no_instance_verified`
otherwise. A solution the reference rejects still fails the whole evaluation
immediately, tolerated or not.

Solutions are checked before the runner's exit status is consulted, so a
rejected solution is a rejection even when the run later timed out or crashed.
`reason` separates model rejection (`invalid_solution`, `suboptimal_solution`,
`objective_mismatch`, `no_solution`) from inconclusive runs (`reference_timeout`,
`execution_timeout`, `memory_limit`, `execution_error`), protocol violations (`invalid_output`, `output_limit`)
and infrastructure failure (`infrastructure_error`).

## Setup

Python 3.12, `requirements.txt`, and a running Docker Linux engine (or podman or
Apptainer; see below). Images
target linux/amd64 and pin their solver versions. Build them explicitly —
`evaluate()` never builds or installs anything:

```sh
python -m evaluation.build                      # every integration, or name specific ids
python -m evaluation.check examples/abbots.py --problem abbots_puzzle --solver cpmpy_python
python -m evaluation.check examples/abbots.py --problem abbots_puzzle --solver cpmpy_python --solution-limit 2
```

### Container engines: Docker, podman, Apptainer

On a new machine, run `make engine` once. It checks the three engines, sets up the one
you pick, and saves the choice for this checkout in `.dcp-engine.json`. For Apptainer
it installs an unprivileged Apptainer from the Apptainer PPA (Ubuntu, no root) and
enables lingering. For podman it writes the configuration below. Then it lists which
images are current and how to get the rest, and runs a smoke test.
`make engine-check` only reports.

[`engine.py`](engine.py) runs the images on one of the three engines. `DCP_ENGINE` picks it
(`docker`, `podman` or `apptainer`); unset, the saved choice applies, else the first one on
`PATH`. `DCP_APPTAINER`, `DCP_APPTAINER_IMAGES` and `DCP_TASKSET` override saved
settings the same way. Each
result's `engine` field records the engine, its version, and how it enforced the CPU
limit: `cpu_limit` is `quota` (a CPU-time quota, as Docker sets) or `cores`. With
`cores`, the run gets `ceil(cpus)` whole cores of its own, and its affinity can't be
widened because `sched_setaffinity` fails. The cores come from `DCP_TASKSET` (e.g.
`0-7`), or else every core the evaluator may use. A run that finds no free core fails
as an `infrastructure_error`, so run at most pool ÷ `ceil(cpus)` evaluations at once.
An admin can make it `quota` by delegating the `cpu` controller to users
(`Delegate=cpu cpuset io memory pids` in a drop-in for `user@.service`).

**Docker** is the reference: the readiness checks and the CI use it.

**Rootless podman** builds from the same Dockerfiles. It also works for a user
without an `/etc/subuid` range or `cpu` delegation (tested with podman 3.4 and all
integrations). It needs `gcc` once, `fuse-overlayfs` and `taskset`, and this
configuration:

```toml
# ~/.config/containers/storage.conf: graphroot on a local disk, not NFS
[storage]
driver = "overlay"
graphroot = "/local/disk/containers"
[storage.options.overlay]
mount_program = "/usr/bin/fuse-overlayfs"
ignore_chown_errors = "true"        # only needed without a subuid range

# ~/.config/containers/registries.conf: resolve bare names like docker does
unqualified-search-registries = ["docker.io"]
short-name-mode = "permissive"
```

Without a subuid range, candidates run as root inside the container. That root is
still the unprivileged host user, and every other restriction is kept
(`test_isolation` checks the host mapping, not the uid). Builds squash every file's
owner to root, so export Docker-built images for other machines rather than these.

**Apptainer** (unprivileged, 1.1 or later) is for machines with neither. It can't
build from a Dockerfile. Build and export the images where Docker or podman runs:

```sh
python -m evaluation.build cpmpy_python
python -m evaluation.export --to exported/ cpmpy_python     # exported/cpmpy_python.tar
```

then copy the folder over and convert it into `DCP_APPTAINER_IMAGES` (default
`images/`). The SIF keeps the recipe label, so readiness compares the same recipe:

```sh
export DCP_ENGINE=apptainer DCP_APPTAINER=/path/to/bin/apptainer   # if not on PATH
python -m evaluation.build --archive exported/ cpmpy_python       # images/cpmpy_python.sif
```

An unprivileged user can't set cgroup limits or a seccomp filter on Apptainer
directly. So each run is a transient `systemd-run --user` service, which bounds memory
(no swap), tasks and CPUs, and records the kernel's OOM kill. This needs a systemd user
manager. On a server whose ssh sessions don't start one, enable lingering once with
`loginctl enable-linger`. The evaluator finds the manager under `/run/user/$UID`.

The container has:

- no network;
- a read-only image and `/input`;
- no capabilities;
- your own uid;
- a per-run scratch directory as `/tmp`.

That `/tmp` is bounded by the disk, not by 512 MB as under Docker. An image's identity
is the SHA-256 of its SIF file.

Rootless podman and Apptainer both need a systemd user session that outlives your
logins, or they fail once you log out. For podman you can set
`cgroup_manager = "cgroupfs"` under `[engine]` in
`~/.config/containers/containers.conf` instead. `--memory` limits and their
`memory_limit` verdicts work on every engine.

The CLI prints one JSON result and exits 0 on acceptance, 1 otherwise. The
Python API is `from evaluation import evaluate`. Call it under an
`if __name__ == "__main__":` guard — reference checks spawn a child process.

Select instances with `--instance-count 3` or `--instance-ids example json:1`.
IDs are original JSON indices; an instance identical to an earlier one has no
ID of its own. Identity uses only the reference's declared data fields; names
and notes do not increase coverage. The first distinct record retains its
metadata. A count is a budget like `solution_limit`: asking for more instances
than exist checks every one that exists, and `instances_available` reports the
supply. A named `--instance-ids` that does not exist is still an error.

| Limit | Default | Flag |
| --- | --- | --- |
| Execution, per instance | 60 s | `--execution-timeout` |
| Reference operation | 60 s | `--reference-timeout` |
| C++ compilation | 120 s | `--compilation-timeout` |
| Memory | 2048 MiB | `--memory-mb` |
| CPUs | 1 | `--cpus` |

Candidate wall-clock adds a 10 s container-startup allowance; solver time is
limited separately inside the runner. Reference time covers process startup
plus each check, and a check may need both a feasibility and an optimality
solve. Output is capped at 8 MiB per stream and container scratch at 512 MiB.

Results carry per-instance outcomes, `instances_available`,
`unperformed_instances`, `skipped_instances`, limits, timings, model/reference/instance hashes, and
the image actually executed: its local ID and the recipe digest that
`evaluation.build` labelled it with (see `generation/README.md`). Only the
recipe means the same on another machine.
Evaluation stops at the first failure, so `instances_checked` counts only
passes — inspect `instances` for the one that failed. Wall time includes
startup and compilation, so it is not comparable to the runner's
`solve_seconds`.

### Solver licences

A commercial solver's licence is never built into an image. The integration declares it
under `licence` in `metadata.json` (see `skills/solver-setup/references/integration.md`),
and each machine says where its own copy is, outside the repository:

```sh
make licences                                         # which licences this machine has
python -m evaluation.licences todo                    # the missing ones, and how to get them
python -m evaluation.licences set hexaly ~/.config/dcp-rosetta/licences/hexaly/license.dat
python -m evaluation.licences check hexaly            # file checks, then a pilot solve
```

`set` saves the path in `.dcp-licences.json` (per checkout, like `.dcp-engine.json`), and
`DCP_LICENCE_<ID>` overrides it. Keep the file at mode 600.

Configure only a licence that works in a container. A named-user licence tied to one host
fails with a host-ID mismatch, because a run has no network and so no host ID. Gurobi's WLS
needs internet while it runs. A size-limited solver such as Gurobi falls back to its free
edition when nothing is configured, so leave it unset rather than point it at such a licence.
`solvers/<solver>/LICENCE.md` says which licences work for that solver and how to get them.

[`licences.py`](licences.py) binds each run its licence read-only, with the solver's
variables:
- a key file as a per-run copy in a private temporary directory;
- a licensed install directly;
- a licence server through a Unix-socket relay, so the run keeps `--network=none`.

What a run prints is redacted before it is parsed or stored: the licence's lines and its
host path become `[licence redacted]`. A submission can read the licence, but cannot
carry it into a result. Results name only the edition: `licence` is `licensed` or
`size-limited`.

A licence failure is never the model's fault. Without the licence configured, an
integration that needs one stops with `licence_unavailable` before any container
starts. When the solver refuses its licence (a message listed under `errors`), the
reason is also `licence_unavailable`. `generation` then neither counts the attempt nor
offers the integration's pairs until the licence works.

## Submitting a model

Pick an integration: any integration folder (`solvers/<solver>/<interface>/`) with a `metadata.json`. What a model
must do, for every integration, is the submission contract
[solvers/CONTRACT.md](../solvers/CONTRACT.md); how a given integration takes it
(file, entrypoint, instance, outputs, objective) is the `CONTRACT.md` in its folder.
Each integration folder holds `metadata.json`, `run.py`, a `Dockerfile`, the
`readiness_test.py` that certifies it, that contract, and a standalone skill for
the solver under `solvers/<solver>/skills/`.

Models are instance-agnostic. Python implements `build(instance)`, C++
implements `Build(instance, model, outputs)`, MiniZinc declares matching data
parameters and emits JSON, an ASP program reads facts and shows atoms, and a
Prolog program defines `model/3` or `model/4` over the instance dict. PuLP
implements `build(instance)` returning an `LpProblem`.
Working examples live in `tests/fixtures/`.

Only the entrypoint file is copied into the container; its parent directory is
never mounted. v1 accepts one file.

## Runner protocol

The image entrypoint receives `/input/model.<ext>` and `/input/request.json`
(`instance`, `solution_limit`, `execution_timeout`, `compilation_timeout`,
`legacy`, `outputs`) and writes JSONL to stdout, logs to stderr. `outputs` lists
the reference's declared output names, for a runner whose language cannot use
them verbatim — an ASP predicate cannot start with a capital, so `clingo_asp`
maps each key to the predicate with its first letter after any leading underscores
lowered. The names are
already in the brief a modeller works from, and no solution is ever included:

```json
{"type":"solution","values":{"x":0,"y":2},"objective":2}
{"type":"status","status":"limit","solve_seconds":0.01}
```

Solution records are followed by exactly one status. For an optimisation, a solution record carries
`objective`, the solution's objective value **in the problem's own terms**: the value the problem's
objective takes on this solution, as the reference computes it. That is the model's objective, which must
be the problem's own (see [solvers/CONTRACT.md](../solvers/CONTRACT.md)), and not whatever the solver
reports internally: a MaxSAT solver's cost of falsified soft clauses, a maximisation the solver negated
to minimise, an objective without the constant its preprocessing dropped. Where the solver's value is not
the problem's, the runner translates it, or computes it from the solution with the model's objective
expression. Integrations at `protocol_version` 2 must report it; earlier ones may.

During an optimisation search a runner may also report each improving solution it finds, before proving
the optimum, as it finds it (flushed, so a run cut off at its limit keeps them):

```json
{"type":"incumbent","objective":12,"seconds":0.31}
```

`objective` is the solution's integer objective value in the problem's own terms, as for a solution record,
`seconds` the time since the search started (after the model was built), nondecreasing. Incumbents come anywhere before the status and are evidence for
anytime measures, never results: the evaluator checks their shape, keeps them per instance as `incumbents`
(`[[seconds, objective], ...]`) and otherwise ignores them. They carry no values.

| Status | Meaning |
| --- | --- |
| `limit` | requested solution count reached |
| `complete` | enumeration exhausted |
| `timeout` | budget spent, or optimum unproven |
| `unsat` | no solution exists |
| `error` / `unsupported` / `compilation_error` | see `detail` |

A runner need not report memory exhaustion itself. The evaluator reads
Docker's `OOMKilled` flag on the exited container, which the kernel sets when
it kills any process in it at the memory limit: the runner, or a solver
process the runner started and then reported as an error. A run that fails
after such a kill is `memory_limit`, whatever status the runner gave. Docker
can set the flag a moment after the container exits, so after an exit 137 the
evaluator reads it again for up to 2 s, and the detail of the failed run gives
both readings.

Zero solutions never pass. Returning fewer than N distinct solutions requires
`complete`, which is the runner's report that the *submitted* model has no more
— it is not read as a claim about the reference. Anything less from a runner
that neither reached the count nor reported exhaustion is `invalid_output`.
Optimization runners emit only final optimal outputs (and, optionally, incumbent
records along the way); the evaluator re-derives optimality itself and never trusts a claimed objective.
It does check every reported objective against the reference, after the solutions are accepted: a solution's
`objective` must be the reference's optimum, and the incumbents must improve and end at it. Otherwise the
run is `objective_mismatch`: the model's objective is scaled, offset or negated, or the runner reports the
solver's internal value. Curves of improving solutions are only comparable across solvers because of this.

## Adding an integration

Add a `solvers/<solver>/<interface>/` directory implementing the protocol, plus smoke tests, and
a `CONTRACT.md` documenting how it realises [solvers/CONTRACT.md](../solvers/CONTRACT.md).
The evaluator dispatches on integration ID, never on language name. Metadata
declares `id`, `image`, `extension`, `enumeration`, descriptive
language/framework/solver fields, and optionally `compilation: true` to
allocate the separate compilation budget. Installation belongs in the
Dockerfile. Shared container code lives in `runner/`, which every image copies;
`runner/requirements.txt` locks the Python solver stack of the CPMpy and
OR-Tools integrations; the other Python integrations keep their own lock beside
their Dockerfile. Every lock carries the hash of each wheel, written from a
certified image by `python -m evaluation.lock`, and Debian and Ubuntu packages
come from the snapshot archive (`solvers/apt-snapshot.sh`), so a rebuild
anywhere installs what was certified.

Containers run with no network, a read-only root, an unprivileged user, no
added capabilities, `no-new-privileges`, and memory/CPU/PID caps. Reference
checking happens in a separate trusted host process the container never sees.

A future problem-specific converter must run inside this same container, with
every staged file in the artifact hash — never on the host, and never by
mounting a submission directory.

## The reference loader

The loader lives with the problems in DCP-Bench Open, at
`bench/dcp_bench/reference.py`, and the evaluator imports it from there; its own
tests and the dataset audit run in that repository.

References are trusted dataset scripts. The loader parses the AST, substitutes
instance values for the marked `# Data` section, and drops the solve/output
tail — that tail never executes. Declared outputs are mapped back to reference
expressions and bound with CPMpy equality constraints, never by running
candidate-generated Python.

Exact keys and array shapes are required. Integer outputs need JSON integers;
Boolean outputs accept JSON Booleans or 0/1. Auxiliary variables are completed
by the reference solver. Instances must supply every data-section field; extra
`name`/`note` metadata keys are ignored.

## Legacy compatibility

`eval.py` (JSONL CLI, JSON to `summary.txt`) routes through this package.
Legacy framework names map onto integrations (CPMpy, OR-Tools, MiniZinc);
anything else fails explicitly rather than running as arbitrary host Python.
It gets the embedded example and one solution only, so it cannot produce a
record that belongs under `generated_models/` — `generation/manage.py` is what
retains a model.

## Validation

```sh
python -m unittest tests.test_evaluation -v
```

The dataset audit runs in `bench/`: all references must load, the first instance
entry must equal the embedded example exactly, every listed instance must build
the reference, and only `name`/`note` extra keys are permitted.

```sh
(cd bench && python -m unittest tests.test_dataset -v)
```

Two checks are opt-in:

```sh
DCP_CONTAINER_TESTS=1 python -m unittest tests.test_solvers -v   # needs built images
(cd bench && DCP_UNSAT_AUDIT=1 python -m unittest tests.test_dataset.ReferenceTests.test_no_unsat_instances)
```

Skipped container tests are not evidence of end-to-end success: the container
run is the authoritative one.

Dataset changes and the reasoning behind them are recorded in
[SOURCES.md](https://github.com/DCP-Bench/DCP-Bench-Open/blob/main/SOURCES.md) in DCP-Bench.

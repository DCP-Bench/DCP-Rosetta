"""Readiness checks for the picat integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver picat` runs this and keeps its
output as the readiness evidence.

`standalone_run` and `standalone_run_no_data` are what a reader does: run dcp_convert_picat.py on a list of
instances (the dataset file's form), then `picat model.pi <data file>` in the image, once per file, with the run
block the contract gives, and read the answer it prints. The converter runs in the image too.

Every check runs the cp module; the sat_* checks repeat satisfaction,
enumeration and minimisation with `import sat.`, because the driver reaches
the solver through whichever module the submission imported and the two must
both work.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate, improving_incumbents
from evaluation.execution import image_identity, integration, run_process
from evaluation.results import EvaluationError

SOLVER = "picat"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions.
REFERENCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")
# The problem's own objective, with a constant term (optimum 3 + 2n = 7) and with a negative optimum (2 - 10 = -8):
# every reported objective must be that value.
CONSTANT_MAXIMIZING = OPTIMIZING.replace("model.minimize(x + y)", "model.maximize(3 + x + y)")
NEGATIVE_MINIMIZING = OPTIMIZING.replace("model.minimize(x + y)", "model.minimize(x + y - 10)")

GOOD = """import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [].
"""
# The objective is an expression, so the driver's own objective variable is
# exercised as well as the direction.
OPTIMAL = """import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #>= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [$OBJECTIVE(X + Y)].
"""
# A free auxiliary variable doubles every solution unless distinctness is
# measured over the declared outputs only.
AUXILIARY = """import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    Z :: 0..1,
    X + Y #= N,
    Vars = [X, Y, Z],
    Outputs = [x = X, y = Y],
    Options = [].
"""
# Outputs that are not Name = Value pairs: the driver must refuse them rather
# than print something the evaluator would have to guess at.
MALFORMED = """import cp.

model(_Data, Vars, Outputs, Options) =>
    Vars = [],
    Outputs = not_a_pair_list,
    Options = [].
"""
UNSATISFIABLE = """import cp.

model(_Data, Vars, Outputs, Options) =>
    X :: 0..1,
    X #= 5,
    Vars = [X],
    Outputs = [x = X, y = 2],
    Options = [].
"""
SLOW = """import cp.

model(_Data, Vars, Outputs, Options) =>
    spin(0),
    X :: 0..1,
    Vars = [X],
    Outputs = [x = X, y = 0],
    Options = [].

spin(N) => spin(N + 1).
"""
# Every claim the evaluator makes about the sandbox, asserted from inside it:
# an unprivileged user, no dataset, only the two staged files, a read-only root
# and no network. Picat has no sockets, so the network probe runs through the
# image's Python, started with command/1.
ISOLATED = r"""import cp.
import os.
import util.

model(Data, Vars, Outputs, Options) =>
    Status = read_file_lines("/proc/self/status"),
    UidMap = read_file_lines("/proc/self/uid_map"),
    % unprivileged on the host: Docker runs as nobody; rootless podman without a subuid range can only run as
    % container root, which maps to the invoking user (the first uid map line does not map 0 to 0)
    (membchk("Uid:\t65534\t65534\t65534\t65534", Status)
    ; membchk("Uid:\t0\t0\t0\t0", Status), UidMap = [Line|_], Fields = split(Line), Fields[2] != "0"),
    not exists("/dataset"),
    sort(listdir("/input")) == sort([".", "..", "model.pi", "request.json"]),
    not writable("/probe.txt"),
    command("python -c \"import socket, sys; s = socket.socket(); s.settimeout(0.5); sys.exit(0 if s.connect_ex(('1.1.1.1', 443)) else 1)\"") == 0,
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [].

writable(Path) => catch((FD = open(Path, write), close(FD)), _, fail).
"""


RUN_BLOCK_DATA = """
main([File]) =>
    Fd = open(File),
    Term = read_term(Fd),
    Term = $json_object(Keys, Values),
    close(Fd),
    Data = new_map([K = V : {K, V} in zip(Keys, Values)]),
    model(Data, Vars, Outputs, Options),
    solve(Options, Vars),
    solve(vars(Outputs)),
    foreach(Name = Value in Outputs)
        printf("%w = %w\\n", Name, Value)
    end.
"""
RUN_BLOCK_NO_DATA = """
main =>
    model(new_map(), Vars, Outputs, Options),
    solve(Options, Vars),
    solve(vars(Outputs)),
    foreach(Name = Value in Outputs)
        printf("%w = %w\\n", Name, Value)
    end.
"""
NO_DATA_MODEL = """import cp.

model(_Data, Vars, Outputs, Options) =>
    [X, Y] :: 0..2,
    X + Y #= 2,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [].
"""
STANDALONE_INSTANCES = [{"n": 2, "name": "two"}, {"n": 3, "name": "three"}]


def standalone_run(temp, with_data):
    """The reader's path, in the image: convert a list of instances with dcp_convert_picat.py, then run
    `picat model.pi <data file>` on each file (or `picat model.pi` for a model with no data)."""
    staging = temp / ("standalone_data" if with_data else "standalone_no_data")
    staging.mkdir()
    (staging / "model.pi").write_text((GOOD + RUN_BLOCK_DATA) if with_data else (NO_DATA_MODEL + RUN_BLOCK_NO_DATA),
                                      encoding="utf-8")
    runs = ["/opt/picat/picat model.pi"]
    if with_data:
        (staging / "instances.json").write_text(json.dumps(STANDALONE_INSTANCES), encoding="utf-8")
        runs = [f"/opt/picat/picat model.pi instances_{i}.dat" for i in range(1, len(STANDALONE_INSTANCES) + 1)]
    staging.chmod(0o777)
    for path in staging.iterdir():
        path.chmod(0o666)
    script = ("python /opt/runner/dcp_convert_picat.py instances.json >/dev/null && " if with_data else "") + " && ".join(runs)
    code, out, err = run_process([
        "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only",
        "--user=65534:65534", "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--tmpfs", "/tmp:rw,exec,nosuid,size=536870912,mode=1777",
        "--mount", f"type=bind,source={staging},target=/w",
        "--workdir=/w", "--env=HOME=/tmp", "--entrypoint", "sh",
        integration(SOLVER)["image"], "-c", script], 300)
    if code or out.count("x = ") != len(runs) or out.count("y = ") != len(runs):
        print((err or out)[-400:], file=sys.stderr)
        return False
    return True


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / name
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(f"{name}.pi", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        def exhausted(name, source, solutions):
            result = check(name, source, solution_limit=5)
            results[name] = (results[name]
                             and result["instances"][0]["solutions_received"] == solutions
                             and result["instances"][0]["runner_status"]["status"] == "complete")

        sat = lambda source: source.replace("import cp.", "import sat.")

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        # x+y==2 has exactly three solutions, so asking for more must come back
        # as exhaustion rather than as a shortfall the evaluator would reject.
        exhausted("exhausted_enumeration", GOOD, 3)
        exhausted("distinct_declared_outputs", AUXILIARY, 3)
        check("minimization", OPTIMAL.replace("OBJECTIVE", "min"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "max"), reference=MAXIMIZING)
        check("sat_satisfaction", sat(GOOD), instances=[{"n": 3, "optimize": False}], instance_count=2)
        exhausted("sat_exhausted_enumeration", sat(AUXILIARY), 3)
        check("sat_minimization", sat(OPTIMAL.replace("OBJECTIVE", "min")), reference=OPTIMIZING)
        check("sat_maximization", sat(OPTIMAL.replace("OBJECTIVE", "max")), reference=MAXIMIZING)
        # Labelling x then y upwards first finds x+y=2, which a maximisation improves on, so each module's
        # $report must yield 2, 3, then the optimum 4.
        for name, module in (("incumbents_maximize", lambda source: source), ("sat_incumbents", sat)):
            results[name] = improving_incumbents(
                check(name, module(OPTIMAL.replace("OBJECTIVE", "max")), reference=MAXIMIZING), minimize=False)
        # Labelling downwards first finds x+y=4, which the minimisation improves on, down to the optimum 2.
        results["incumbents"] = improving_incumbents(
            check("incumbents", OPTIMAL.replace("$OBJECTIVE(X + Y)", "$min(X + Y), down"), reference=OPTIMIZING))
        # Acceptance implies every reported objective (solutions and incumbents) equalled the reference's optimum,
        # under each module.
        results["objective_values"] = all(
            check("objective_values", module(OPTIMAL.replace("$OBJECTIVE(X + Y)", objective)), reference=reference,
                  solution_limit=3)["accepted"]
            for module in (lambda source: source, sat)
            for objective, reference in (("$max(3 + X + Y)", CONSTANT_MAXIMIZING),
                                         ("$min(X + Y - 10)", NEGATIVE_MINIMIZING)))
        # a standalone model carries a run block (main/1 over one file name); the driver's own main/1 takes two
        check("run_block_ignored", GOOD + RUN_BLOCK_DATA)
        results["standalone_run"] = standalone_run(temp, True)
        results["standalone_run_no_data"] = standalone_run(temp, False)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

    try:
        image_identity({"id": SOLVER, "image": "dcp-eval/definitely-absent:readiness"})
        results["missing_image"] = False
    except EvaluationError as error:
        results["missing_image"] = error.reason == "infrastructure_error"

    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

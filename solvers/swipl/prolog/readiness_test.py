"""Readiness checks for the swipl_clpfd integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver swipl_clpfd` runs this and keeps
its output as the readiness evidence.

`standalone_run` and `standalone_run_no_data` are what a reader does: `swipl -g "solve_file('<file>')" -t halt model.pl`
(or `solve_model(_{})` for a model with no data) in the image, with the run block the contract gives, on a list of
instances (the dataset file's form), and read the answer it prints.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from evaluation import evaluate
from evaluation.execution import image_identity, integration, run_process
from evaluation.results import EvaluationError

SOLVER = "swipl_clpfd"

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

HEADER = ":- use_module(library(clpfd)).\n"
GOOD = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                 "    N = Instance.n,\n"
                 "    [X, Y] ins 0..N,\n"
                 "    X + Y #= N.\n")
OPTIMAL = HEADER + ("model(Instance, [X, Y], [x-X, y-Y], OBJECTIVE(X + Y)) :-\n"
                    "    N = Instance.n,\n"
                    "    [X, Y] ins 0..N,\n"
                    "    X + Y #>= N.\n")
# Outputs that are not Name-Value pairs: the driver must refuse them rather than
# print something the evaluator would have to guess at.
MALFORMED = HEADER + "model(_, [], not_a_pair_list).\n"
UNSATISFIABLE = HEADER + ("model(_, [X], [x-X, y-2]) :-\n"
                          "    X in 0..1,\n"
                          "    X #= 5.\n")
SLOW = HEADER + ("model(_, [X], [x-X, y-0]) :-\n"
                 "    sleep(120),\n"
                 "    X in 0..1.\n")
# Every claim the evaluator makes about the sandbox, asserted from inside it:
# an unprivileged user, no dataset, only the two staged files, a read-only root
# and no network.
ISOLATED = HEADER + (
    ":- use_module(library(socket)).\n"
    "model(Instance, [X, Y], [x-X, y-Y]) :-\n"
    "    read_file_to_string('/proc/self/status', Status, []),\n"
    "    split_string(Status, '\\n', '', Lines),\n"
    "    read_file_to_string('/proc/self/uid_map', UidMap, []),\n"
    "    % unprivileged on the host: Docker runs as nobody; rootless podman without a subuid range can only run as\n"
    "    % container root, which maps to the invoking user (the uid map is not the identity)\n"
    "    (   memberchk(\"Uid:\\t65534\\t65534\\t65534\\t65534\", Lines)\n"
    "    ;   memberchk(\"Uid:\\t0\\t0\\t0\\t0\", Lines),\n"
    "        \\+ sub_string(UidMap, _, _, _, \"0          0 4294967295\")\n"
    "    ),\n"
    "    \\+ exists_directory('/dataset'),\n"
    "    directory_files('/input', Files),\n"
    "    msort(Files, ['.', '..', 'model.pl', 'request.json']),\n"
    "    \\+ catch(open('/probe.txt', write, _), _, fail),\n"
    "    \\+ catch(tcp_connect('1.1.1.1':443, _, []), _, fail),\n"
    "    N = Instance.n,\n"
    "    [X, Y] ins 0..N,\n"
    "    X + Y #= N.\n")


RUN_BLOCK = """
:- use_module(library(http/json)).

% Reads the data file, builds the model for its first instance (or the N-th), solves it and prints each output.
solve_file(File) :- solve_file(File, 1).
solve_file(File, N) :-
    setup_call_cleanup(open(File, read, Stream),
                       json_read_dict(Stream, Data, [value_string_as(atom)]),
                       close(Stream)),
    (   is_list(Data) -> nth1(N, Data, Instance) ; Instance = Data ),
    solve_model(Instance).

solve_model(Instance) :-
    (   current_predicate(model/4)
    ->  model(Instance, Vars, Outputs, Objective)
    ;   model(Instance, Vars, Outputs), Objective = none
    ),
    (   current_predicate(labeling_options/1) -> labeling_options(Options) ; Options = [ff] ),
    term_variables(Vars-Outputs, All),
    (   Objective == none
    ->  labeling(Options, All)
    ;   once(labeling([Objective|Options], All))
    ),
    forall(member(Name-Value, Outputs), format("~w = ~w~n", [Name, Value])).
"""
NO_DATA_MODEL = HEADER + ("model(_, [X, Y], [x-X, y-Y]) :-\n"
                          "    [X, Y] ins 0..2,\n"
                          "    X + Y #= 2.\n")
STANDALONE_INSTANCES = [{"n": 2, "optimize": False}, {"n": 3, "optimize": True}]


def standalone_run(temp, with_data):
    """The reader's path, in the image: `swipl -g "solve_file('<file>')" -t halt model.pl` on the dataset file's
    form (a list of instances), the second instance too; `solve_model(_{})` for a model with no data."""
    staging = temp / ("standalone_data" if with_data else "standalone_no_data")
    staging.mkdir()
    (staging / "model.pl").write_text((GOOD + RUN_BLOCK) if with_data else (NO_DATA_MODEL + RUN_BLOCK), encoding="utf-8")
    goals = ["solve_model(_{})"]
    if with_data:
        (staging / "instances.json").write_text(json.dumps(STANDALONE_INSTANCES), encoding="utf-8")
        goals = ["solve_file('instances.json')", "solve_file('instances.json', 2)"]
    staging.chmod(0o777)
    for path in staging.iterdir():
        path.chmod(0o666)
    script = " && ".join(f"swipl --no-tty -g \"{goal}\" -t halt model.pl" for goal in goals)
    code, out, err = run_process([
        "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only",
        "--user=65534:65534", "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--tmpfs", "/tmp:rw,exec,nosuid,size=536870912,mode=1777",
        "--mount", f"type=bind,source={staging},target=/w",
        "--workdir=/w", "--env=HOME=/tmp", "--entrypoint", "sh",
        integration(SOLVER)["image"], "-c", script], 300)
    if code or out.count("x = ") != len(goals) or out.count("y = ") != len(goals):
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
            result = evaluate(candidate(f"{name}.pl", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        # x+y==2 has exactly three solutions, so asking for more must come back
        # as exhaustion rather than as a shortfall the evaluator would reject.
        exhausted = check("exhausted_enumeration", GOOD, solution_limit=5)
        results["exhausted_enumeration"] = (
            results["exhausted_enumeration"]
            and exhausted["instances"][0]["solutions_received"] == 3
            and exhausted["instances"][0]["runner_status"]["status"] == "complete")
        check("minimization", OPTIMAL.replace("OBJECTIVE", "min"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "max"), reference=MAXIMIZING)
        # Acceptance implies every reported objective equalled the reference's optimum.
        results["objective_values"] = (
            check("objective_values", OPTIMAL.replace("OBJECTIVE(X + Y)", "max(3 + X + Y)"),
                  reference=CONSTANT_MAXIMIZING, solution_limit=3)["accepted"]
            and check("objective_values", OPTIMAL.replace("OBJECTIVE(X + Y)", "min(X + Y - 10)"),
                      reference=NEGATIVE_MINIMIZING, solution_limit=3)["accepted"])
        # a standalone model carries a run block (solve_file/1,2, solve_model/1); the driver ignores it
        check("run_block_ignored", GOOD + RUN_BLOCK)
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

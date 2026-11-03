# csplib_007_all_interval: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Find a series of the pitch-classes 0 to n-1, each occurring once, in which the
    intervals between neighbouring notes cover every interval from 1 to n-1 once."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series

    model = cp_model.CpModel()

    # x[i] is the pitch-class of the note at position i
    x = [model.new_int_var(0, n - 1, f"x_{i}") for i in range(n)]
    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = [model.new_int_var(1, n - 1, f"diffs_{i}") for i in range(n - 1)]

    # The series is a permutation of the pitch-classes.
    model.add_all_different(x)
    # The intervals are a permutation of 1 to n-1.
    model.add_all_different(diffs)
    # Each interval is the distance between two neighbouring notes.
    for i in range(n - 1):
        model.add_abs_equality(diffs[i], x[i + 1] - x[i])

    return model, {"x": x, "diffs": diffs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

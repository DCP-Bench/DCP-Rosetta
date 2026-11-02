# csplib_007_all_interval: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import z3


def create_model(instance):
    """Find a series of the pitch-classes 0 to n-1, each occurring once, in which the
    intervals between neighbouring notes cover every interval from 1 to n-1 once."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series

    # x[i] is the pitch-class of the note at position i
    x = [z3.Int(f"x_{i}") for i in range(n)]
    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = [z3.Int(f"diffs_{i}") for i in range(n - 1)]

    solver = z3.Solver()

    # Pitch-classes and intervals stay within their ranges.
    solver.add([z3.And(pitch >= 0, pitch <= n - 1) for pitch in x])
    solver.add([z3.And(step >= 1, step <= n - 1) for step in diffs])

    # The series uses each pitch-class once.
    solver.add(z3.Distinct(x))

    # The intervals are all different, so they are the intervals 1 to n-1 in some order.
    solver.add(z3.Distinct(diffs))

    # Each interval is the distance between two neighbouring notes.
    solver.add([diffs[i] == z3.Abs(x[i + 1] - x[i]) for i in range(n - 1)])

    return solver, {"x": x, "diffs": diffs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

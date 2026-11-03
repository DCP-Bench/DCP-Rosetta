# csplib_007_all_interval: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

from exact import Exact


def create_model(instance):
    """Find a series of the pitch-classes 0 to n-1, each occurring once, in which the
    intervals between neighbouring notes cover every interval from 1 to n-1 once."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series

    solver = Exact()

    # x[i] is the pitch-class of the note at position i
    x = [f"x_{i}" for i in range(n)]
    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = [f"diffs_{i}" for i in range(n - 1)]
    # is_pitch[i][a] is 1 when the note at position i is pitch-class a, and 0 when not
    is_pitch = [{} for _ in range(n)]
    # is_interval[i][d] is 1 when the interval between positions i and i + 1 is d, and 0 when not
    is_interval = [{} for _ in range(n - 1)]

    # Exact identifies its variables by name.
    for i in range(n):
        solver.addVariable(x[i], 0, n - 1)
        for a in range(n):
            is_pitch[i][a] = f"is_pitch_{i}_{a}"
            solver.addVariable(is_pitch[i][a], 0, 1)
    for i in range(n - 1):
        solver.addVariable(diffs[i], 1, n - 1)
        for d in range(1, n):
            is_interval[i][d] = f"is_interval_{i}_{d}"
            solver.addVariable(is_interval[i][d], 0, 1)

    # Each position holds exactly one pitch-class.
    for i in range(n):
        solver.addConstraint([(1, is_pitch[i][a]) for a in range(n)], True, 1, True, 1)
        # x[i] is that pitch-class.
        solver.addConstraint([(a, is_pitch[i][a]) for a in range(1, n)] + [(-1, x[i])], True, 0, True, 0)

    # Each gap between neighbouring positions has exactly one interval.
    for i in range(n - 1):
        solver.addConstraint([(1, is_interval[i][d]) for d in range(1, n)], True, 1, True, 1)
        # diffs[i] is that interval.
        solver.addConstraint([(d, is_interval[i][d]) for d in range(1, n)] + [(-1, diffs[i])], True, 0, True, 0)

    # Each pitch-class is used by exactly one position.
    for a in range(n):
        solver.addConstraint([(1, is_pitch[i][a]) for i in range(n)], True, 1, True, 1)
    # No interval occurs in two gaps.
    for d in range(1, n):
        solver.addConstraint([(1, is_interval[i][d]) for i in range(n - 1)], False, 0, True, 1)

    # If the notes at positions i and i + 1 are a and b, the interval between them is |a - b|.
    for i in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    solver.addConstraint([(1, is_pitch[i][a]), (1, is_pitch[i + 1][b]), (-1, is_interval[i][abs(a - b)])],
                                         False, 0, True, 1)

    return solver, {"x": x, "diffs": diffs}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

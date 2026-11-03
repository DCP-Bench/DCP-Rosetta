# csplib_076_costas_arrays: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_076_costas_arrays.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_076_costas_arrays.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_076_costas_arrays.py csplib_076_costas_arrays.json

from exact import Exact


def create_model(instance):
    """Place n marks on an n by n grid, one mark in each row and one in each column, so that
    the n(n-1)/2 vectors between pairs of marks are all different (a Costas array)."""
    n_marks = instance["n"]  # the grid is n_marks by n_marks

    solver = Exact()

    # Exact identifies its variables by name.
    # costas[i] is the column (1 to n_marks) of the mark in row i
    costas = [f"costas_{i}" for i in range(n_marks)]
    for name in costas:
        solver.addVariable(name, 1, n_marks)

    # at[i][v] is 1 when the mark in row i is in column v, and 0 otherwise
    at = [{v: f"at_{i}_{v}" for v in range(1, n_marks + 1)} for i in range(n_marks)]
    for i in range(n_marks):
        for name in at[i].values():
            solver.addVariable(name, 0, 1)
        # each row has exactly one mark, and costas[i] is its column
        solver.addConstraint([(1, name) for name in at[i].values()], True, 1, True, 1)
        solver.addConstraint([(v, at[i][v]) for v in range(1, n_marks + 1)] + [(-1, costas[i])], True, 0, True, 0)
    # each column has exactly one mark
    for v in range(1, n_marks + 1):
        solver.addConstraint([(1, at[i][v]) for i in range(n_marks)], True, 1, True, 1)

    # For each gap between rows, the differences between the columns of the marks that many
    # rows apart are all different.
    max_diff = n_marks - 1
    for gap in range(1, n_marks - 1):
        n_pairs = n_marks - gap
        # diff[i][d] is 1 when the column of the mark in row i + gap minus the column of the mark in row i is d
        diff = [{d: f"diff_{gap}_{i}_{d}" for d in range(-max_diff, max_diff + 1)} for i in range(n_pairs)]
        for i in range(n_pairs):
            for name in diff[i].values():
                solver.addVariable(name, 0, 1)
            # each pair of marks has exactly one difference
            solver.addConstraint([(1, name) for name in diff[i].values()], True, 1, True, 1)
            # the difference is the one just defined; two marks in different rows share no column, so it is never 0
            solver.addConstraint([(d, diff[i][d]) for d in range(-max_diff, max_diff + 1) if d != 0]
                                 + [(-1, costas[i + gap]), (1, costas[i])], True, 0, True, 0)
        # no difference occurs for two pairs at this gap
        for d in range(-max_diff, max_diff + 1):
            solver.addConstraint([(1, diff[i][d]) for i in range(n_pairs)], False, 0, True, 1)

    return solver, {"costas": costas}


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

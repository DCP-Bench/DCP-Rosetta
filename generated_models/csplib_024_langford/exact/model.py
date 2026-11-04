# csplib_024_langford: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

from exact import Exact


def create_model(instance):
    """Langford's pairing problem: arrange two copies of each number 1 to k in a row of 2k places,
    so that the two copies of each number i have exactly i other numbers between them."""
    k = instance["k"]  # the largest number; there are k numbers, two copies each
    length = 2 * k     # the number of places in the row

    solver = Exact()

    # Exact identifies its variables by name.
    # sol[pos] is the number at place pos, with the places counted from 0
    sol = [f"sol_{pos}" for pos in range(length)]
    for name in sol:
        solver.addVariable(name, 1, k)

    # first[i, p] is 1 when the first copy of number i is at place p, and 0 when not.
    # The second copy then sits i + 1 places further on, so p can only run up to length - i - 2.
    first = {}
    for i in range(1, k + 1):
        for p in range(length - i - 1):
            first[i, p] = f"first_{i}_at_{p}"
            solver.addVariable(first[i, p], 0, 1)

    # Each number has exactly one first copy, which fixes where both of its copies are.
    for i in range(1, k + 1):
        solver.addConstraint([(1, first[i, p]) for p in range(length - i - 1)], True, 1, True, 1)

    for pos in range(length):
        # The first and second copies that could sit at place pos, each with its number.
        covering = []
        for i in range(1, k + 1):
            if (i, pos) in first:
                covering.append((i, first[i, pos]))
            if (i, pos - i - 1) in first:
                covering.append((i, first[i, pos - i - 1]))
        # Each place holds exactly one copy.
        solver.addConstraint([(1, name) for _, name in covering], True, 1, True, 1)
        # The number at place pos is the number of the copy that sits there.
        solver.addConstraint(covering + [(-1, sol[pos])], True, 0, True, 0)

    return solver, {"sol": sol}


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

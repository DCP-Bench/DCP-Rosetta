# csplib_084_hadamard_matrix: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_084_hadamard_matrix.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_084_hadamard_matrix.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_084_hadamard_matrix.py csplib_084_hadamard_matrix.json

from exact import Exact


def create_model(instance):
    """Find two sequences a and b of odd length n_entries, with entries -1 or +1, that each sum
    to 1 and whose periodic autocorrelations add up to -2 at every shift s from 1 to n_shifts
    (a Legendre pair)."""
    n_entries = instance["l"]        # length l of each sequence, an odd number
    n_shifts = (n_entries - 1) // 2  # the shifts s = 1 to n_shifts are constrained

    solver = Exact()

    # Exact identifies its variables by name.
    def sequence(name):
        # plus[i] is 1 when entry i is +1, and 0 when it is -1
        plus = [f"{name}_plus_{i}" for i in range(n_entries)]
        # values[i] is entry i of the sequence, -1 or +1
        values = [f"{name}_{i}" for i in range(n_entries)]
        for i in range(n_entries):
            solver.addVariable(plus[i], 0, 1)
            solver.addVariable(values[i], -1, 1)
            # the entry is 2 * plus[i] - 1, so it is never 0
            solver.addConstraint([(1, values[i]), (-2, plus[i])], True, -1, True, -1)
        # the entries sum to 1, so (n_entries + 1) / 2 of them are +1
        solver.addConstraint([(1, p) for p in plus], True, (n_entries + 1) // 2, True, (n_entries + 1) // 2)
        return plus, values

    def agreements(name, plus, s):
        # same[i] is 1 when entry i and entry i + s (modulo n_entries) are equal, and 0 otherwise
        same = [f"{name}_same_{s}_{i}" for i in range(n_entries)]
        for i in range(n_entries):
            p, q = plus[i], plus[(i + s) % n_entries]
            solver.addVariable(same[i], 0, 1)
            # same[i] is 1 exactly when both entries are +1 or both are -1
            solver.addConstraint([(1, same[i]), (1, p), (1, q)], True, 1)
            solver.addConstraint([(1, same[i]), (-1, p), (-1, q)], True, -1)
            solver.addConstraint([(1, same[i]), (1, p), (-1, q)], False, 0, True, 1)
            solver.addConstraint([(1, same[i]), (-1, p), (1, q)], False, 0, True, 1)
        return same

    plus_a, a = sequence("a")
    plus_b, b = sequence("b")

    # For each shift s, PAF(a, s) + PAF(b, s) = -2. Each PAF is 2 times the number of equal
    # pairs minus n_entries, so the equal pairs of a and b together number n_entries - 1.
    for s in range(1, n_shifts + 1):
        same = agreements("a", plus_a, s) + agreements("b", plus_b, s)
        solver.addConstraint([(1, name) for name in same], True, n_entries - 1, True, n_entries - 1)

    return solver, {"a": a, "b": b}


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

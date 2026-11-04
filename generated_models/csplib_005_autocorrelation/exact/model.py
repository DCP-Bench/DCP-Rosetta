# csplib_005_autocorrelation: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from exact import Exact


def create_model(instance):
    """Choose a binary sequence of n values, each +1 or -1, that minimises the sum of the
    squared periodic autocorrelations C_k = sum_i S_i * S_((i+k) mod n), for k = 1 to n-1."""
    n = instance["n"]  # the length of the sequence

    solver = Exact()

    # Exact identifies its variables by name.
    # plus[i] is 1 when S_i is +1, and 0 when S_i is -1
    plus = [f"plus_{i}" for i in range(n)]
    # sequence[i] is the bit S_i, either -1 or +1
    sequence = [f"sequence_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(plus[i], 0, 1)
        solver.addVariable(sequence[i], -1, 1)
        # S_i is 2 * plus[i] - 1
        solver.addConstraint([(1, sequence[i]), (-2, plus[i])], True, -1, True, -1)

    # same[(i, j)] is 1 exactly when S_i and S_j are equal, for i < j. Two equal bits multiply to
    # +1 and two different bits to -1, so each correlation counts its agreeing pairs.
    same = {}
    for i in range(n):
        for j in range(i + 1, n):
            name = f"same_{i}_{j}"
            same[(i, j)] = name
            solver.addVariable(name, 0, 1)
            solver.addConstraint([(1, name), (1, plus[i]), (1, plus[j])], True, 1)  # both -1
            solver.addConstraint([(1, name), (-1, plus[i]), (-1, plus[j])], True, -1)  # both +1
            solver.addConstraint([(1, name), (1, plus[i]), (-1, plus[j])], False, 0, True, 1)  # -1, +1
            solver.addConstraint([(1, name), (-1, plus[i]), (1, plus[j])], False, 0, True, 1)  # +1, -1

    # The correlation C_k is 2 * (agreeing pairs) - n, over the pairs (i, (i + k) mod n). Its square is
    # read off which number of agreeing pairs holds, one 0/1 variable per possible number v.
    # Only k <= n / 2 is modelled, because C_k and C_(n-k) use the same pairs. Shift n / 2 counts once,
    # the others twice. The number of agreeing pairs has the same parity as n, since the positions split
    # into cycles under i -> i + k and the bit changes along each cycle come in pairs.
    energy = []  # the terms of E = sum_k C_k^2, as (weight, variable) pairs
    for k in range(1, n // 2 + 1):
        weight = 1 if 2 * k == n else 2
        pairs = [same[(min(i, (i + k) % n), max(i, (i + k) % n))] for i in range(n)]
        counts = [v for v in range(n + 1) if (n - v) % 2 == 0]
        count_is = {v: f"correlation_{k}_has_{v}_agreeing_pairs" for v in counts}
        for name in count_is.values():
            solver.addVariable(name, 0, 1)
        # exactly one number of agreeing pairs holds
        solver.addConstraint([(1, name) for name in count_is.values()], True, 1, True, 1)
        # the agreeing pairs number the chosen v
        solver.addConstraint([(1, name) for name in pairs] + [(-v, name) for v, name in count_is.items() if v],
                             True, 0, True, 0)
        # C_k^2 = (2v - n)^2; a zero correlation adds nothing to E
        energy += [(weight * (2 * v - n) ** 2, name) for v, name in count_is.items() if 2 * v != n]

    # Minimise E.
    solver.setObjective(energy, minimize=True)

    return solver, {"sequence": sequence}


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

# broken_weights: a cvc5 (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python broken_weights.py broken_weights.json

import cvc5.pythonic as c5


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]  # the total weight of the unbroken weight, in pounds
    n = instance["n"]  # the number of pieces it broke into

    # pick[k][a] is true when piece k weighs a pounds
    pick = [{a: c5.Bool(f"pick_{k}_{a}") for a in range(1, m + 1)} for k in range(n)]
    # weights[k] is the weight of piece k, in pounds
    weights = [c5.Int(f"weights_{k}") for k in range(n)]

    # Linear integer logic: cvc5 solves this model much faster than with the default Solver().
    solver = c5.SolverFor("QF_LIA")

    # Each piece takes exactly one weight from 1 to m, and that is its weight.
    for k in range(n):
        solver.add(c5.Sum([c5.If(pick[k][a], 1, 0) for a in range(1, m + 1)]) == 1)
        solver.add(weights[k] == c5.Sum([c5.If(pick[k][a], a, 0) for a in range(1, m + 1)]))

    # The pieces add up to the whole weight.
    solver.add(c5.Sum(weights) == m)

    # reach[k][v] is true when the first k pieces can be put on the two pans of a balance
    # so that the difference between the two pans is v pounds.
    reach = [{v: c5.Bool(f"reach_{k}_{v}") for v in range(-m, m + 1)} for k in range(n + 1)]

    # With no pieces, the pans differ by 0 pounds only.
    for v in range(-m, m + 1):
        solver.add(reach[0][v] if v == 0 else c5.Not(reach[0][v]))

    # A difference of v with the first k pieces needs a difference with the first k - 1
    # pieces, with piece k either off the pans or on one pan.
    for k in range(1, n + 1):
        for v in range(-m, m + 1):
            options = [reach[k - 1][v]]
            for a in range(1, m + 1):
                if -m <= v - a <= m:
                    options.append(c5.And(pick[k - 1][a], reach[k - 1][v - a]))
                if -m <= v + a <= m:
                    options.append(c5.And(pick[k - 1][a], reach[k - 1][v + a]))
            body = options[0] if len(options) == 1 else c5.Or(options)
            solver.add(c5.Implies(reach[k][v], body))

    # Every load from 1 to m can be weighed: the pans can differ by that load.
    for t in range(1, m + 1):
        solver.add(reach[n][t])

    return solver, {"weights": weights}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

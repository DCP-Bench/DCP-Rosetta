# broken_weights: a Python-MIP (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python broken_weights.py broken_weights.json

import mip


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]  # the weight of the unbroken measure, in pounds
    n_pieces = instance["n"]  # the number of pieces it broke into

    model = mip.Model(solver_name="CBC")

    # the heaviest a piece can be, since each of the other pieces weighs at least 1 pound
    max_weight = m - (n_pieces - 1)
    # the whole-pound weights a piece can have
    values = range(1, max_weight + 1)

    # x[i][v] is 1 when piece i weighs v pounds, and 0 when not
    x = [
        {v: model.add_var(f"x_{i}_{v}", var_type=mip.BINARY) for v in values}
        for i in range(n_pieces)
    ]
    # weights[i] is the weight of piece i, in pounds
    weights = []
    for i in range(n_pieces):
        # each piece has exactly one weight
        model.add_constr(mip.xsum(x[i][v] for v in values) == 1)
        # the weight of piece i is the weight it was given
        w = model.add_var(f"w_{i}", lb=1, ub=max_weight, var_type=mip.INTEGER)
        model.add_constr(w == mip.xsum(v * x[i][v] for v in values))
        weights.append(w)

    # the pieces together weigh the whole measure
    model.add_constr(mip.xsum(weights) == m)

    # count[v] is the number of pieces weighing v pounds
    count = {}
    # used[v] is 1 when some piece weighs v pounds, and 0 when not
    used = {}
    for v in values:
        count[v] = mip.xsum(x[i][v] for i in range(n_pieces))
        used[v] = model.add_var(f"used_{v}", var_type=mip.BINARY)
        # a weight is used only when some piece has it
        model.add_constr(count[v] <= n_pieces * used[v])

    # The pieces lighter than a used weight v weigh S pounds in total, and balance every load
    # up to S. A piece of weight v extends that to S + v exactly when v <= 2S + 1, so every
    # used weight must satisfy this.
    for v in values:
        # the total weight of the pieces lighter than v, in pounds
        lighter = mip.xsum(u * count[u] for u in values if u < v)
        model.add_constr(v * used[v] <= 2 * lighter + 1)

    return model, {"weights": weights}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

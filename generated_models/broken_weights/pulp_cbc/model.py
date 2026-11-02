# broken_weights: a PuLP (Python) model from DCP Rosetta.
# Download the `broken_weights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/broken_weights.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python broken_weights.py broken_weights.json

import pulp


def create_model(instance):
    """A merchant's measuring weight of m pounds broke into n pieces, each a whole number
    of pounds. On a balance scale the pieces must weigh every whole load from 1 to m."""
    m = instance["m"]         # the total weight of the unbroken weight, in pounds
    n_pieces = instance["n"]  # the number of pieces it broke into

    problem = pulp.LpProblem("broken_weights", pulp.LpMinimize)

    # Every other piece weighs at least 1 pound, so no piece weighs more than this.
    max_piece = m - (n_pieces - 1)
    # The weights a piece can have, in pounds
    sizes = range(1, max_piece + 1)

    # weights[j] is the weight of piece j, in pounds
    weights = [pulp.LpVariable(f"weights_{j}", 1, max_piece, cat="Integer")
               for j in range(n_pieces)]

    # The pieces add up to the whole weight.
    problem += pulp.lpSum(weights) == m

    # is_weight[j][v] is 1 when piece j weighs v pounds, and 0 when not.
    is_weight = [{v: pulp.LpVariable(f"is_weight_{j}_{v}", cat="Binary") for v in sizes}
                 for j in range(n_pieces)]
    # count[v] is the number of pieces that weigh v pounds.
    count = {v: pulp.LpVariable(f"count_{v}", 0, n_pieces, cat="Integer") for v in sizes}

    # Each piece has exactly one weight, and it is the weight given in weights.
    for j in range(n_pieces):
        problem += pulp.lpSum(is_weight[j].values()) == 1
        problem += weights[j] == pulp.lpSum(v * is_weight[j][v] for v in sizes)

    # count[v] is the number of pieces of weight v.
    for v in sizes:
        problem += count[v] == pulp.lpSum(is_weight[j][v] for j in range(n_pieces))

    # Every load t from 1 to m can be weighed.
    for t in range(1, m + 1):
        # net[v] is the number of pieces of weight v on the other pan minus the number on
        # the pan with the object. Pieces of one weight can be split between the two pans,
        # so net[v] lies between -count[v] and count[v].
        net = {v: pulp.LpVariable(f"net_{t}_{v}", -n_pieces, n_pieces, cat="Integer")
               for v in sizes}
        for v in sizes:
            problem += net[v] <= count[v]
            problem += net[v] >= -count[v]
        # The pieces balance the load when their net weight is t pounds.
        problem += pulp.lpSum(v * net[v] for v in sizes) == t

    return problem, {"weights": weights}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

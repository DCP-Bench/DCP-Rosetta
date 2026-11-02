# bales_of_hay: a PuLP (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python bales_of_hay.py bales_of_hay.json

import itertools

import pulp


def create_model(instance):
    """Bales of hay were weighed in every combination of two, and the weights of the
    pairs were written down in numerical order without saying which pair gave which
    weight. Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the weight of each pair of bales that was written down

    problem = pulp.LpProblem("bales_of_hay", pulp.LpMinimize)

    # no bale weighs more than this
    heaviest_bale = 50

    # bales[i] is the weight of bale i
    bales = [pulp.LpVariable(f"bale_{i}", 0, heaviest_bale, cat="Integer") for i in range(n)]

    # every pair of different bales, as (i, j) with i < j
    pairs = list(itertools.combinations(range(n), 2))

    # Large enough that the bounds on a pair's sum do not bind for a pair that is not
    # the one giving the written weight.
    slack = 2 * heaviest_bale + max(weights)

    for position, weight in enumerate(weights):
        # pick[(i, j)] is 1 when the pair of bales i and j gives this written weight, and 0 when not
        chosen = {}
        for i, j in pairs:
            pick = pulp.LpVariable(f"pick_{position}_{i}_{j}", cat="Binary")
            chosen[(i, j)] = pick
            problem += bales[i] + bales[j] <= weight + slack * (1 - pick)
            problem += bales[i] + bales[j] >= weight - slack * (1 - pick)

        # Each written weight is the total weight of exactly one pair of bales.
        problem += pulp.lpSum(chosen.values()) == 1

    return problem, {"bales": bales}


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

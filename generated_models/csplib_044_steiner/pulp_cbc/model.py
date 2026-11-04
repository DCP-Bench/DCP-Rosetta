# csplib_044_steiner: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

import itertools

import pulp


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]          # the number of elements
    n_sets = n * (n - 1) // 6  # the number of triples in the system

    problem = pulp.LpProblem("steiner", pulp.LpMinimize)  # the puzzle asks for triples only: no objective

    # sets[i][j] is 1 when element j belongs to triple i, and 0 when not
    sets = pulp.LpVariable.dicts("sets", (range(n_sets), range(n)), cat="Binary")

    # Each triple has three elements.
    for i in range(n_sets):
        problem += pulp.lpSum(sets[i][j] for j in range(n)) == 3

    # Each pair of elements lies in at most one triple.
    for u, v in itertools.combinations(range(n), 2):
        covers = []
        for i in range(n_sets):
            # together is 1 when triple i contains both u and v, and 0 when not
            together = pulp.LpVariable(f"pair_{i}_{u}_{v}", cat="Binary")
            problem += together >= sets[i][u] + sets[i][v] - 1
            problem += together <= sets[i][u]
            problem += together <= sets[i][v]
            covers.append(together)
        problem += pulp.lpSum(covers) <= 1

    # the triples as a matrix, one row for each triple
    rows = [[sets[i][j] for j in range(n)] for i in range(n_sets)]
    return problem, {"sets": rows}


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

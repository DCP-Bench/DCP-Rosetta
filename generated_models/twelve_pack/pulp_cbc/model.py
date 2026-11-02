# twelve_pack: a PuLP (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python twelve_pack.py twelve_pack.json

import pulp


def create_model(instance):
    """Given a target number of items, find the combination of packs of different sizes
    that meets or exceeds the target with as few items as possible."""
    target = instance["target"]  # the number of items needed
    packs = instance["packs"]    # packs[i]: the number of items in a pack of kind i
    n_kinds = len(packs)

    # No best purchase buys more packs of one kind than the target, since that many packs
    # alone already reach it. Twice the target is a safe upper limit.
    max_per_kind = 2 * target

    problem = pulp.LpProblem("twelve_pack", pulp.LpMinimize)

    # counts[i] is how many packs of kind i are bought.
    counts = [pulp.LpVariable(f"counts_{i}", 0, max_per_kind, cat="Integer")
              for i in range(n_kinds)]

    # total is the number of items bought.
    total = pulp.LpVariable("total", 0, max_per_kind * n_kinds, cat="Integer")

    # The total is the number of items in all the packs bought.
    problem += total == pulp.lpSum(packs[i] * counts[i] for i in range(n_kinds))

    # The items bought meet or exceed the target.
    problem += total >= target

    # The objective: as few items as possible.
    problem += total

    return problem, {"counts": counts}


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

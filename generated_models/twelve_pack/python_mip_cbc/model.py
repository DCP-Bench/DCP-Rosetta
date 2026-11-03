# twelve_pack: a Python-MIP (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python twelve_pack.py twelve_pack.json

import mip


def create_model(instance):
    """Given a target number of items and several pack sizes, buy packs of the different
    sizes so that the items meet or exceed the target, using as few items as possible."""
    packs = instance["packs"]      # packs[i] is the number of items in a pack of kind i
    target = instance["target"]    # the number of items needed
    n_kinds = len(packs)           # the number of pack kinds
    max_pack = max(packs)          # the largest pack

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # counts[i] is how many packs of kind i are bought. An optimal purchase has fewer than
    # target + max_pack items, since otherwise one pack could be left out and the target
    # still met. That bounds each count.
    counts = [
        model.add_var(f"counts_{i}", lb=0, ub=(target + max_pack) // packs[i], var_type=mip.INTEGER)
        for i in range(n_kinds)
    ]

    # The number of items bought.
    items = mip.xsum(packs[i] * counts[i] for i in range(n_kinds))

    # The items bought meet or exceed the target.
    model += items >= target

    # Buy as few items as possible.
    model.objective = items

    return model, {"counts": counts}


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

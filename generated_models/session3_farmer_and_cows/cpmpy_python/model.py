# session3_farmer_and_cows: a CPMpy model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. He distributes the cows over his sons, each son
    receiving the given number of cows, so that every son gets the same total
    quantity of milk."""
    num_cows = instance["num_cows"]          # the number of cows, numbered 1..num_cows
    num_sons = instance["num_sons"]          # the number of sons, numbered 0..num_sons-1
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: how many cows son s receives

    # milk[i]: the milk given by cow i+1, equal to its number
    milk = np.arange(1, num_cows + 1)
    # every son must get an equal part of all the milk
    milk_per_son = milk.sum() // num_sons

    # cow_assignments[i] is the son who receives cow i+1
    cow_assignments = cp.intvar(0, num_sons - 1, shape=num_cows, name="cow_assignments")

    model = cp.Model()
    for son in range(num_sons):
        # Each son receives the prescribed number of cows.
        model.add(cp.sum(cow_assignments == son) == cows_per_son[son])
        # Each son's cows give the same total quantity of milk.
        model.add(cp.sum((cow_assignments == son) * milk) == milk_per_son)

    return model, {"cow_assignments": cow_assignments}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

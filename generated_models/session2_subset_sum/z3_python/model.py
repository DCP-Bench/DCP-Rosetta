# session2_subset_sum: a Z3 (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

import z3


def create_model(instance):
    """A bank van had several kinds of bags of coins, with a fixed number of
    coins in each kind and many bags of each kind. Thieves stole some bags
    holding a given total number of coins; find how many bags of each kind were
    stolen."""
    coins = instance["coin_numbers"]      # coins[i]: the number of coins in a bag of kind i
    total = instance["total_coins_lost"]  # the total number of coins that were lost

    # bags[i]: the number of stolen bags of kind i
    bags = [z3.Int(f"bags_{i}") for i in range(len(coins))]

    solver = z3.Solver()

    # A count of bags is never negative, and each bag holds at least one coin,
    # so no kind can account for more bags than there are lost coins.
    solver.add([z3.And(0 <= b, b <= total) for b in bags])

    # The stolen bags hold exactly the coins that were lost.
    solver.add(z3.Sum([c * b for c, b in zip(coins, bags)]) == total)

    return solver, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

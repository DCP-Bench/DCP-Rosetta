# session2_subset_sum: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install ortools`):
#   python session2_subset_sum.py session2_subset_sum.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A bank van had several kinds of bags of coins, with a fixed number of
    coins in each kind and many bags of each kind. Thieves stole some bags holding
    a given total number of coins; find how many bags of each kind were stolen."""
    coins = instance["coin_numbers"]      # coins[i]: the number of coins in a bag of kind i
    total = instance["total_coins_lost"]  # the total number of coins that were lost

    model = cp_model.CpModel()

    # bags[i]: the number of stolen bags of kind i. Every bag holds at least
    # one coin, so no kind can account for more bags than there are lost coins.
    bags = [model.new_int_var(0, total, f"bags_{i}") for i in range(len(coins))]

    # The stolen bags hold exactly the coins that were lost.
    model.add(sum(c * b for c, b in zip(coins, bags)) == total)

    return model, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

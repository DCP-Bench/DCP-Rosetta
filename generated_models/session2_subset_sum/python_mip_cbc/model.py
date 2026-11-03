# session2_subset_sum: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

import mip


def create_model(instance):
    """A bank van had several kinds of bags of coins, each kind holding a fixed
    number of coins, with many bags of each kind. Thieves stole some of the bags,
    and together they held a given total number of coins. Find how many bags of
    each kind were stolen."""
    coin_numbers = instance["coin_numbers"]  # coin_numbers[i]: the number of coins in a bag of kind i
    total_coins_lost = instance["total_coins_lost"]  # the number of coins that were stolen
    n_kinds = len(coin_numbers)  # the number of kinds of bag

    model = mip.Model(solver_name="CBC")

    # bags[i] is the number of stolen bags of kind i. Every bag holds at least one
    # coin, so a kind cannot account for more bags than fit in the total.
    bags = [
        model.add_var(f"bags_{i}", lb=0, ub=total_coins_lost // coin_numbers[i], var_type=mip.INTEGER)
        for i in range(n_kinds)
    ]

    # The stolen bags hold exactly the coins that were lost.
    model.add_constr(mip.xsum(coin_numbers[i] * bags[i] for i in range(n_kinds)) == total_coins_lost)

    return model, {"bags": bags}


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

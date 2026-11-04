# session2_subset_sum: a cvc5 (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

import cvc5.pythonic as c5


def create_model(instance):
    """A bank van lost some bags of coins, each bag holding one of the given
    numbers of coins, with several bags of each kind. Find how many bags of each
    kind were stolen so that exactly the given total number of coins was lost."""
    coin_numbers = instance["coin_numbers"]    # coin_numbers[i]: the number of coins in a bag of kind i
    total_lost = instance["total_coins_lost"]  # the total number of coins that were stolen

    # bags[i]: the number of stolen bags of kind i
    bags = [c5.Int(f"bags_{i}") for i in range(len(coin_numbers))]

    solver = c5.Solver()

    # A count is not negative. Each bag holds at least one coin, so a kind
    # cannot have more than total // coins bags stolen.
    for bag, coins_per_bag in zip(bags, coin_numbers):
        solver.add(bag >= 0)
        solver.add(bag <= total_lost // coins_per_bag)

    # The stolen bags hold exactly the coins that were lost.
    solver.add(c5.Sum([coins * bag for coins, bag in zip(coin_numbers, bags)]) == total_lost)

    return solver, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

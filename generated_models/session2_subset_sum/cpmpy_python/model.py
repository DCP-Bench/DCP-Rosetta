# session2_subset_sum: a CPMpy model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session2_subset_sum.py session2_subset_sum.json

import cpmpy as cp


def create_model(instance):
    """A bank van lost some bags of coins, each bag holding one of the given
    numbers of coins, with several bags of each kind. Find how many bags of each
    kind were stolen so that exactly the given total number of coins was lost."""
    coin_numbers = instance["coin_numbers"]      # coin_numbers[i]: the number of coins in a bag of kind i
    total_lost = instance["total_coins_lost"]    # the total number of coins that were stolen

    # bags[i] is the number of stolen bags of kind i; no kind can account for
    # more bags than there are coins lost, since every bag holds at least one coin
    bags = cp.intvar(0, total_lost, shape=len(coin_numbers), name="bags")

    model = cp.Model()
    # The stolen bags hold exactly the coins that were lost.
    model.add(cp.sum(bags * coin_numbers) == total_lost)

    return model, {"bags": bags}


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

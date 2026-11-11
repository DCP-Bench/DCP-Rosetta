# session2_subset_sum: a PyCSP3 model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session2_subset_sum.py session2_subset_sum.json

from pycsp3 import *


def create_model(instance):
    """A bank van had several bags of coins, each containing a number of coins from a given
    list (there are multiple bags of the same kind). Thieves stole some bags, and a given
    total number of coins was lost. Find how many bags were stolen for each type of coin bag."""
    coin_numbers = instance["coin_numbers"]          # coin_numbers[i]: the number of coins in a bag of type i
    total_coins_lost = instance["total_coins_lost"]  # the total number of coins lost
    n_types = len(coin_numbers)

    # bags[i] is the number of stolen bags of type i. Every bag is taken to hold at least one coin
    # (assumed), so the stolen bags of a type hold at most total_coins_lost coins and their number is at most
    # total_coins_lost // coin_numbers[i].
    bags = VarArray(size=n_types, dom=lambda i: range(total_coins_lost // coin_numbers[i] + 1))

    satisfy(
        # The stolen bags hold exactly the total number of coins lost.
        Sum(coin_numbers[i] * bags[i] for i in range(n_types)) == total_coins_lost
    )

    return {"bags": bags}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

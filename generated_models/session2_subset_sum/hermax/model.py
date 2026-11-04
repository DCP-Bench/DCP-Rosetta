# session2_subset_sum: a hermax (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install hermax`):
#   python session2_subset_sum.py session2_subset_sum.json

from hermax.model import Model


def create_model(instance):
    """A bank van held several bags of coins, each bag type holding a fixed number of coins.
    Thieves stole some bags, losing a given total number of coins. Find how many bags of
    each type were stolen, so that the stolen bags hold exactly the lost coins."""
    coins = instance["coin_numbers"]          # coins[i]: the number of coins in one bag of type i
    total = instance["total_coins_lost"]      # total: the number of coins that were lost

    m = Model()
    # bags[i] is how many bags of type i were stolen; a type cannot give more bags than fit in the total
    bags = [m.int(f"bags_{i}", 0, total // coins[i]) for i in range(len(coins))]

    # The stolen bags hold exactly the lost number of coins.
    m &= (sum(coins[i] * bags[i] for i in range(len(coins))) == total)

    return m, {"bags": bags}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

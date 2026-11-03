# session2_subset_sum: a PuLP (Python) model from DCP Rosetta.
# Download the `session2_subset_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subset_sum.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session2_subset_sum.py session2_subset_sum.json

import pulp


def create_model(instance):
    """A bank van lost some bags of coins, each bag holding one of the given
    numbers of coins, with several bags of each kind. Find how many bags of each
    kind were stolen so that exactly the given total number of coins was lost."""
    coin_numbers = instance["coin_numbers"]  # coin_numbers[i]: the number of coins in a bag of kind i
    total_lost = instance["total_coins_lost"]  # the total number of coins that were lost

    problem = pulp.LpProblem("subset_sum", pulp.LpMinimize)

    # bags[i] is the number of stolen bags of kind i. No kind can account for more
    # bags than there are coins lost, since every bag holds at least one coin.
    bags = [pulp.LpVariable(f"bags_{i}", 0, total_lost, cat="Integer") for i in range(len(coin_numbers))]

    # The stolen bags hold exactly the coins that were lost.
    problem += pulp.lpSum(coin_numbers[i] * bags[i] for i in range(len(coin_numbers))) == total_lost

    return problem, {"bags": bags}


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

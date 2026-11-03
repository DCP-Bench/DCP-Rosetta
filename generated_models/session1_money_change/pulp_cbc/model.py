# session1_money_change: a PuLP (Python) model from DCP Rosetta.
# Download the `session1_money_change.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_money_change.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session1_money_change.py session1_money_change.json

import pulp


def create_model(instance):
    """Alice has to give Bob change. She has coins of several types, each
    worth a fixed value and available in a limited number. Make up the amount
    from the coins she has, using as few coins as possible."""
    amount = instance["amount"]                    # the change Bob is owed
    types_of_coins = instance["types_of_coins"]    # types_of_coins[i]: the value of coin type i
    available_coins = instance["available_coins"]  # available_coins[i]: how many coins of type i Alice has
    n_types = len(types_of_coins)                  # the number of coin types

    problem = pulp.LpProblem("change", pulp.LpMinimize)

    # coin_counts[i] is the number of coins of type i given to Bob
    coin_counts = [pulp.LpVariable(f"coin_count_{i}", 0, available_coins[i], cat="Integer")
                   for i in range(n_types)]

    # The coins given to Bob add up to the amount.
    problem += pulp.lpSum(types_of_coins[i] * coin_counts[i] for i in range(n_types)) == amount

    # Use as few coins as possible.
    problem += pulp.lpSum(coin_counts)

    return problem, {"coin_counts": coin_counts}


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

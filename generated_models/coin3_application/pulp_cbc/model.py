# coin3_application: a PuLP (Python) model from DCP Rosetta.
# Download the `coin3_application.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coin3_application.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python coin3_application.py coin3_application.json

import pulp


def create_model(instance):
    """Find the minimum number of coins that allows one to pay exactly any amount
    smaller than a given maximum amount, using a given set of denominations."""
    denominations = instance["denominations"]   # denominations[i]: the value of a coin of type i
    max_amount = instance["max_amount_to_pay"]  # every amount below this must be payable
    n = len(denominations)                      # the number of coin types

    problem = pulp.LpProblem("coin3_application", pulp.LpMinimize)

    # x[i] is the number of coins of type i that are carried
    x = [pulp.LpVariable(f"x{i}", 0, max_amount, cat="Integer") for i in range(n)]

    # For each amount, use[i] is the number of coins of type i paid out for it.
    for amount in range(1, max_amount):
        use = [pulp.LpVariable(f"u{amount}_{i}", 0, max_amount, cat="Integer")
               for i in range(n)]
        # Only coins that are carried can be paid out.
        for i in range(n):
            problem += use[i] <= x[i]
        # The coins paid out add up to the amount.
        problem += pulp.lpSum(denominations[i] * use[i] for i in range(n)) == amount

    # Carry as few coins as possible.
    problem += pulp.lpSum(x)

    return problem, {"x": x}


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

# candies: a PuLP (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python candies.py candies.json

import pulp


def create_model(instance):
    """Alice, a kindergarten teacher, gives candies to children sitting in a line, each with a
    rating. Every child gets at least one candy, and of two neighbours the one with the higher
    rating gets more. Minimize the total number of candies."""
    ratings = instance["ratings"]  # ratings[i]: the rating of the child at position i
    n = len(ratings)               # the number of children

    problem = pulp.LpProblem("candies", pulp.LpMinimize)

    # candies[i] is the number of candies the child at position i gets. An optimal share
    # never gives a child more than n.
    candies = [pulp.LpVariable(f"x_{i}", 1, n, cat="Integer") for i in range(n)]
    # total is the number of candies given out, at least one per child
    total = pulp.LpVariable("z", n, n * n, cat="Integer")

    # The total is the sum of the candies given to the children.
    problem += total == pulp.lpSum(candies)

    # Of two neighbours, the child with the higher rating gets at least one candy more.
    # Equal ratings give no rule.
    for i in range(1, n):
        if ratings[i - 1] > ratings[i]:
            problem += candies[i - 1] >= candies[i] + 1
        elif ratings[i - 1] < ratings[i]:
            problem += candies[i - 1] + 1 <= candies[i]

    # Minimize the total number of candies.
    problem += total

    return problem, {"z": total, "x": candies}


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

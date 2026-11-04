# session3_farmer_and_cows: a PuLP (Python) model from DCP Rosetta.
# Download the `session3_farmer_and_cows.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session3_farmer_and_cows.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python session3_farmer_and_cows.py session3_farmer_and_cows.json

import pulp


def create_model(instance):
    """A farmer has cows numbered 1 up to the number of cows, and each cow gives
    as much milk as its number. He divides the cows between his sons, each son
    receiving a given number of cows, so that every son gets the same total
    quantity of milk. Decide which son gets each cow."""
    num_cows = instance["num_cows"]          # the number of cows
    num_sons = instance["num_sons"]          # the number of sons
    cows_per_son = instance["cows_per_son"]  # cows_per_son[s]: the number of cows son s receives

    milk = [i + 1 for i in range(num_cows)]  # milk[i]: the milk from cow i+1, equal to its number
    share = sum(milk) // num_sons            # the milk each son must receive

    problem = pulp.LpProblem("farmer", pulp.LpMinimize)

    # gets[i][s] is 1 when son s receives cow i+1, and 0 when not
    gets = pulp.LpVariable.dicts("gets", (range(num_cows), range(num_sons)), cat="Binary")

    # Each cow goes to exactly one son.
    for i in range(num_cows):
        problem += pulp.lpSum(gets[i][s] for s in range(num_sons)) == 1

    # Each son receives the prescribed number of cows, and his cows give an equal share of the milk.
    for s in range(num_sons):
        problem += pulp.lpSum(gets[i][s] for i in range(num_cows)) == cows_per_son[s]
        problem += pulp.lpSum(milk[i] * gets[i][s] for i in range(num_cows)) == share

    # cow_assignments[i] is the number of the son who receives cow i+1
    cow_assignments = [pulp.LpVariable(f"cow_{i}", 0, num_sons - 1, cat="Integer")
                       for i in range(num_cows)]
    # Each cow's son number is the son it went to.
    for i in range(num_cows):
        problem += cow_assignments[i] == pulp.lpSum(s * gets[i][s] for s in range(num_sons))

    return problem, {"cow_assignments": cow_assignments}


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

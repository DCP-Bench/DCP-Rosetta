# fifty_puzzle: a PuLP (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python fifty_puzzle.py fifty_puzzle.json

import pulp


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs: choose
    the dummies to knock down so that their numbers add up to exactly the target sum,
    neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must add up to exactly
    n_dummies = len(values)              # the number of dummies

    problem = pulp.LpProblem("fifty_puzzle", pulp.LpMinimize)

    # dummies[i] is 1 when dummy i is knocked over, and 0 when it is not
    dummies = [pulp.LpVariable(f"dummies_{i}", cat="Binary") for i in range(n_dummies)]

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    problem += pulp.lpSum(values[i] * dummies[i] for i in range(n_dummies)) == target_sum

    return problem, {"dummies": dummies}


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

# three_sum: a PuLP (Python) model from DCP Rosetta.
# Download the `three_sum.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/three_sum.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python three_sum.py three_sum.json

import pulp


def create_model(instance):
    """Given a collection of integers, find a given number of its elements that
    sum to zero."""
    nums = instance["nums"]  # nums[i]: the i-th integer of the collection
    m = instance["m"]        # how many elements to select
    n_numbers = len(nums)

    problem = pulp.LpProblem("three_sum", pulp.LpMinimize)

    # indices[i] is true when element i is selected.
    indices = [pulp.LpVariable(f"index_{i}", cat="Binary") for i in range(n_numbers)]

    # The selected elements sum to zero.
    problem += pulp.lpSum(v * x for v, x in zip(nums, indices)) == 0

    # Exactly m elements are selected.
    problem += pulp.lpSum(indices) == m

    return problem, {"indices": indices}


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

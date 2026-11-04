# devils_word: a PuLP (Python) model from DCP Rosetta.
# Download the `devils_word.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/devils_word.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python devils_word.py devils_word.json

import pulp


def create_model(instance):
    """Given an array of integers, put a plus or a minus sign in front of each
    integer so that the signed integers add up to the given total."""
    arr = instance["arr"]      # arr[i]: the integer that gets a sign
    total = instance["total"]  # the value the signed integers must add up to
    n_ints = len(arr)          # the number of integers

    problem = pulp.LpProblem("devils_word", pulp.LpMinimize)

    # plus[i] is 1 when arr[i] gets a plus sign and 0 when it gets a minus sign.
    # A zero is the same with either sign, so it always gets a plus sign.
    plus = [
        pulp.LpVariable(f"plus_{i}", lowBound=1 if arr[i] == 0 else 0, upBound=1, cat="Binary")
        for i in range(n_ints)
    ]
    # result[i] is arr[i] with its sign: arr[i] when plus[i] is 1, -arr[i] otherwise.
    result = [arr[i] * (2 * plus[i] - 1) for i in range(n_ints)]

    # The signed integers add up to the total.
    problem += pulp.lpSum(result) == total

    return problem, {"result": result}


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

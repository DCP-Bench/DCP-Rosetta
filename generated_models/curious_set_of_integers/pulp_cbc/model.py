# curious_set_of_integers: a PuLP (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python curious_set_of_integers.py curious_set_of_integers.json

import math

import pulp


def create_model(instance):
    """The integers 1, 3, 8 and 120 form a set in which the product of any two
    integers is one less than a perfect square. Find a fifth number (at least 0)
    that can be added to the set without destroying this property."""
    n = instance["n"]              # the size of the set once the new number is added
    max_val = instance["max_val"]  # the largest value of the new number and of every square root

    known = [1, 3, 8, 120]  # the four numbers of the puzzle
    if n != len(known) + 1:
        # The model adds one number to the four of the puzzle, so n must be five.
        raise ValueError("this model adds exactly one number to the known set")

    problem = pulp.LpProblem("curious_set_of_integers", pulp.LpMinimize)  # the puzzle asks for any such number

    # The new number, from 0 to max_val
    number = pulp.LpVariable("number", 0, max_val, cat="Integer")

    # The new number differs from each of the four numbers: it lies below it or above it.
    for k in known:
        above = pulp.LpVariable(f"above_{k}", cat="Binary")  # 1 when the new number is above k, 0 when below
        problem += number <= k - 1 + (max_val + 1) * above
        problem += number >= k + 1 - (max_val + 1) * (1 - above)

    # The four numbers already share the property. A pair that does not makes the problem infeasible.
    for a in known:
        for b in known:
            if a != b:
                r = math.isqrt(a * b + 1)
                if r * r != a * b + 1 or r > max_val:
                    problem += number <= -1

    # The product of the new number and each of the four numbers is one less than a square.
    for k in known:
        # The roots run up to the largest one whose square is at most k * max_val + 1.
        roots = range(0, min(max_val, math.isqrt(k * max_val + 1)) + 1)
        # root[r] is 1 when k times the new number plus 1 is the square of r
        root = {r: pulp.LpVariable(f"root_{k}_{r}", cat="Binary") for r in roots}
        problem += pulp.lpSum(root.values()) == 1
        problem += k * number + 1 == pulp.lpSum(r * r * var for r, var in root.items())

    return problem, {"number": number}


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

# bowls_and_oranges: a PuLP (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

import pulp


def create_model(instance):
    """n bowls stand in a line at intervals of one metre, numbered 1 to n. Place all the m
    oranges in the bowls, at most one orange per bowl, so that no three oranges A, B and C
    have the distance from A to B equal to the distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls
    n_oranges = instance["m"]  # the number of oranges

    problem = pulp.LpProblem("bowls_and_oranges", pulp.LpMinimize)

    # The oranges are numbered from the lowest bowl up, so orange k has k oranges below it and
    # n_oranges - 1 - k above it, which bounds its bowl.
    low = [k + 1 for k in range(n_oranges)]                       # lowest bowl for orange k
    high = [n_bowls - (n_oranges - 1 - k) for k in range(n_oranges)]  # highest bowl for orange k

    # in_bowl[k][b] is 1 when orange k is in bowl b
    in_bowl = [{b: pulp.LpVariable(f"in_bowl_{k}_{b}", cat="Binary")
                for b in range(low[k], high[k] + 1)}
               for k in range(n_oranges)]

    # x[k] is the bowl holding orange k
    x = [pulp.LpVariable(f"x_{k}", low[k], high[k], cat="Integer") for k in range(n_oranges)]

    # Each orange is in exactly one bowl, and x[k] is that bowl.
    for k in range(n_oranges):
        problem += pulp.lpSum(in_bowl[k].values()) == 1
        problem += x[k] == pulp.lpSum(b * var for b, var in in_bowl[k].items())

    # Each orange is in a higher bowl than the one before it, so no bowl holds two oranges.
    for k in range(n_oranges - 1):
        problem += x[k + 1] >= x[k] + 1

    # occupied[b] is 1 when some orange is in bowl b
    occupied = {b: pulp.lpSum(in_bowl[k][b] for k in range(n_oranges) if b in in_bowl[k])
                for b in range(1, n_bowls + 1)}

    # No three oranges in evenly spaced bowls: among bowls b, b + d and b + 2d, at most two
    # hold an orange.
    for first in range(1, n_bowls + 1):
        for gap in range(1, (n_bowls - first) // 2 + 1):
            problem += (occupied[first] + occupied[first + gap]
                        + occupied[first + 2 * gap]) <= 2

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

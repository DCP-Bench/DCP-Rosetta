# csplib_024_langford: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_024_langford.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_024_langford.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_024_langford.py csplib_024_langford.json

import pulp


def create_model(instance):
    """Arrange two copies of each number from 1 to k in one sequence of 2k places, so that the two
    1's have one number between them, the two 2's have two numbers between them, ..., and the two
    k's have k numbers between them."""
    k = instance["k"]  # the largest number; the sequence holds two copies of each number from 1 to k
    length = 2 * k     # the number of places in the sequence

    problem = pulp.LpProblem("langford", pulp.LpMinimize)

    # start[i][p] is 1 when the first copy of number i is at place p and the second copy at place
    # p + i + 1, and 0 when not. Only places where the second copy still fits are offered.
    start = {i: {p: pulp.LpVariable(f"start_{i}_{p}", cat="Binary")
                 for p in range(length - i - 1)}
             for i in range(1, k + 1)}

    # Each number has exactly one placement.
    for i in range(1, k + 1):
        problem += pulp.lpSum(start[i].values()) == 1

    # Each place holds exactly one number: either the first copy of a number starts there, or the
    # second copy of a number starts i + 1 places earlier.
    holds = []
    for place in range(length):
        covering = []  # the placements that put a copy of some number at this place
        for i in range(1, k + 1):
            if place in start[i]:
                covering.append((i, start[i][place]))
            if place - i - 1 in start[i]:
                covering.append((i, start[i][place - i - 1]))
        problem += pulp.lpSum(var for _, var in covering) == 1
        holds.append(pulp.lpSum(i * var for i, var in covering))

    return problem, {"sol": holds}


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

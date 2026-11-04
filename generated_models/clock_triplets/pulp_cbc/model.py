# clock_triplets: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/clock_triplets.html
# Run it (after `pip install pulp numpy`) with:
#   python clock_triplets.py

import pulp


def create_model(instance):
    """Rearrange the numbers 1 to 12 on the face of a clock so that no three
    adjacent numbers sum to more than 21, the smallest possible largest sum."""
    n = 12  # the numbers on the clock face, 1 to 12, and the positions on it

    problem = pulp.LpProblem("clock_triplets", pulp.LpMinimize)

    # pick[i][v] is 1 when position i of the clock holds the number v
    pick = pulp.LpVariable.dicts("pick", (range(n), range(1, n + 1)), cat="Binary")

    # x[i] is the number at position i of the clock
    x = [pulp.LpVariable(f"x{i}", 1, n, cat="Integer") for i in range(n)]

    # Each position holds exactly one number, and x[i] is that number.
    for i in range(n):
        problem += pulp.lpSum(pick[i][v] for v in range(1, n + 1)) == 1
        problem += x[i] == pulp.lpSum(v * pick[i][v] for v in range(1, n + 1))

    # Each number from 1 to 12 appears on exactly one position.
    for v in range(1, n + 1):
        problem += pulp.lpSum(pick[i][v] for i in range(n)) == 1

    # Every three adjacent numbers, wrapping around the face, sum to at most 21.
    for i in range(n):
        problem += x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= 21

    return problem, {"x": x}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

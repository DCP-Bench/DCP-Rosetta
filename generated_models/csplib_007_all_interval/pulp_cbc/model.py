# csplib_007_all_interval: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_007_all_interval.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_007_all_interval.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_007_all_interval.py csplib_007_all_interval.json

import pulp


def create_model(instance):
    """Arrange the pitch-classes 0 to n-1 in a series, each pitch-class once, so that the
    intervals between neighbouring notes are exactly the intervals 1 to n-1, each once."""
    n = instance["n"]  # the number of pitch-classes, and so of notes in the series

    problem = pulp.LpProblem("all_interval", pulp.LpMinimize)  # a series is asked for, not an optimum: no objective

    # pick[i][v] is 1 when the note at position i is pitch-class v
    pick = pulp.LpVariable.dicts("pick", (range(n), range(n)), cat="Binary")
    # x[i] is the pitch-class of the note at position i
    x = [pulp.LpVariable(f"x_{i}", 0, n - 1, cat="Integer") for i in range(n)]
    for i in range(n):
        # each position holds exactly one pitch-class, and x[i] is that pitch-class
        problem += pulp.lpSum(pick[i][v] for v in range(n)) == 1
        problem += x[i] == pulp.lpSum(v * pick[i][v] for v in range(n))
    # each pitch-class occurs exactly once in the series
    for v in range(n):
        problem += pulp.lpSum(pick[i][v] for i in range(n)) == 1

    # pairs of different pitch-classes (u, v), read as u followed by v
    pairs = [(u, v) for u in range(n) for v in range(n) if u != v]
    # step[(i, u, v)] marks the pair of neighbouring notes at positions i and i + 1 being u
    # then v. The sums below fix it to 0 or 1 without a whole-number domain.
    step = {(i, u, v): pulp.LpVariable(f"step_{i}_{u}_{v}", 0, 1)
            for i in range(n - 1) for (u, v) in pairs}
    for i in range(n - 1):
        for u in range(n):
            # the pair starting at position i starts with the note u exactly when the note at position i is u
            problem += pulp.lpSum(step[(i, u, v)] for v in range(n) if v != u) == pick[i][u]
        for v in range(n):
            # the pair ends with the note at position i + 1
            problem += pulp.lpSum(step[(i, u, v)] for u in range(n) if u != v) == pick[i + 1][v]

    # diffs[i] is the interval between the notes at positions i and i + 1
    diffs = [pulp.LpVariable(f"diffs_{i}", 1, n - 1, cat="Integer") for i in range(n - 1)]
    for i in range(n - 1):
        problem += diffs[i] == pulp.lpSum(abs(u - v) * step[(i, u, v)] for (u, v) in pairs)
    # the intervals are all different: each interval from 1 to n-1 is the gap of exactly one pair of neighbours
    for d in range(1, n):
        problem += pulp.lpSum(
            step[(i, u, v)] for i in range(n - 1) for (u, v) in pairs if abs(u - v) == d) == 1

    return problem, {"x": x, "diffs": diffs}


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

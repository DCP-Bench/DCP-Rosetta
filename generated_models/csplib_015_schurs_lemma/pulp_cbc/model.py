# csplib_015_schurs_lemma: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

import pulp


def create_model(instance):
    """Put n balls labelled 1, ..., n into c boxes so that for any triple of balls
    (x, y, z) with x + y = z, not all three are in the same box."""
    n = instance["n"]  # the number of balls, labelled 1 to n
    c = instance["c"]  # the number of boxes, labelled 1 to c
    boxes = range(1, c + 1)  # the box labels

    # There is no objective: any placement that meets the rule is an answer.
    problem = pulp.LpProblem("schur", pulp.LpMinimize)

    # in_box[i][b] is 1 when ball i+1 is in box b, and 0 when not
    in_box = pulp.LpVariable.dicts("in_box", (range(n), boxes), cat="Binary")

    # Each ball is in exactly one box.
    for i in range(n):
        problem += pulp.lpSum(in_box[i][b] for b in boxes) == 1

    # For x + y = z, the balls x, y and z are not all in the same box. When x equals y,
    # the same ball is counted twice, and the rule still holds.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            for b in boxes:
                problem += in_box[x - 1][b] + in_box[y - 1][b] + in_box[z - 1][b] <= 2

    # balls[i] is the number of the box that ball i+1 is in
    balls = [pulp.LpVariable(f"ball{i}", 1, c, cat="Integer") for i in range(n)]
    # The box number of each ball is the box it is in.
    for i in range(n):
        problem += balls[i] == pulp.lpSum(b * in_box[i][b] for b in boxes)

    return problem, {"balls": balls}


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

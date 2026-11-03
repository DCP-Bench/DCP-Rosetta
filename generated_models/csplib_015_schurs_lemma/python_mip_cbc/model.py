# csplib_015_schurs_lemma: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

import mip


def create_model(instance):
    """Put n balls labelled 1, ..., n into c boxes so that for any triple of balls
    (x, y, z) with x + y = z, not all three are in the same box."""
    n_balls = instance["n"]  # the number of balls, labelled 1, ..., n_balls
    n_boxes = instance["c"]  # the number of boxes, labelled 1, ..., n_boxes

    model = mip.Model(solver_name="CBC")

    # in_box[i][j] is 1 when ball i+1 is in box j+1, and 0 when not
    in_box = [
        [model.add_var(f"in_box_{i}_{j}", var_type=mip.BINARY) for j in range(n_boxes)]
        for i in range(n_balls)
    ]

    # Each ball is in exactly one box.
    for i in range(n_balls):
        model += mip.xsum(in_box[i][j] for j in range(n_boxes)) == 1

    # For every triple x + y = z with z <= n_balls, the balls x, y and z are not all in the same box.
    for x in range(1, n_balls + 1):
        for y in range(1, n_balls + 1):
            z = x + y
            if z > n_balls:
                continue
            for j in range(n_boxes):
                model += mip.xsum([in_box[x - 1][j], in_box[y - 1][j], in_box[z - 1][j]]) <= 2

    # balls[i] is the box of ball i+1, as a number from 1 to n_boxes.
    balls = []
    for i in range(n_balls):
        ball = model.add_var(f"ball_{i}", lb=1, ub=n_boxes, var_type=mip.INTEGER)
        model += ball == mip.xsum((j + 1) * in_box[i][j] for j in range(n_boxes))
        balls.append(ball)

    return model, {"balls": balls}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

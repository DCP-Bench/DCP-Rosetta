# csplib_015_schurs_lemma: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

import cvc5.pythonic as c5


def create_model(instance):
    """Put n balls labelled 1, ..., n into c boxes so that for any triple of balls
    (x, y, z) with x + y = z, not all three are in the same box."""
    n_balls = instance["n"]  # the number of balls, labelled 1, ..., n_balls
    n_boxes = instance["c"]  # the number of boxes, labelled 1, ..., n_boxes

    # balls[i] is the box that ball i+1 is put in
    balls = [c5.Int(f"ball_{i}") for i in range(n_balls)]
    # the rules on the box numbers and on the triples
    solver = c5.Solver()

    # Every ball is put in one of the boxes.
    for ball in balls:
        solver.add(ball >= 1)
        solver.add(ball <= n_boxes)

    # For every triple x + y = z with z <= n_balls, x and y may be equal, the balls x, y
    # and z are not all in the same box.
    for x in range(1, n_balls + 1):
        for y in range(x, n_balls + 1):
            z = x + y
            if z > n_balls:
                break
            for box in range(1, n_boxes + 1):
                solver.add(c5.Or(balls[x - 1] != box, balls[y - 1] != box, balls[z - 1] != box))

    return solver, {"balls": balls}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

# csplib_015_schurs_lemma: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

import z3


def create_model(instance):
    """Put the balls labelled 1, ..., n into c boxes so that for any three balls x, y and
    z with x + y = z, not all three are in the same box."""
    n = instance["n"]  # the number of balls, labelled 1, ..., n
    c = instance["c"]  # the number of boxes, labelled 1, ..., c

    # balls[i] is the box that ball i + 1 is in
    balls = [z3.Int(f"balls_{i}") for i in range(n)]

    solver = z3.Solver()

    # Each ball is in one of the boxes.
    solver.add([z3.And(box >= 1, box <= c) for box in balls])

    # For every x + y = z with z at most n, the balls x, y and z are not all in one box.
    for x in range(1, n):
        for y in range(1, n - x + 1):
            z = x + y
            solver.add(z3.Or(balls[x - 1] != balls[y - 1],
                             balls[x - 1] != balls[z - 1],
                             balls[y - 1] != balls[z - 1]))

    return solver, {"balls": balls}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

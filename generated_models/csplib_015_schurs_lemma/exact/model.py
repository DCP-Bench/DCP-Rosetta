# csplib_015_schurs_lemma: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from exact import Exact


def create_model(instance):
    """Schur's lemma. Put the balls 1, ..., n into the boxes so that no three balls x, y
    and z with x + y = z all lie in the same box."""
    n_balls = instance["n"]  # the number of balls, labelled 1, ..., n_balls
    n_boxes = instance["c"]  # the number of boxes, labelled 1, ..., n_boxes

    solver = Exact()

    # Exact identifies its variables by name.
    # balls[i] is the box that ball i + 1 is in
    balls = [f"ball{i}" for i in range(n_balls)]
    for name in balls:
        solver.addVariable(name, 1, n_boxes)

    # in_box[name][b] is 1 when the ball called `name` is in box b, and 0 when not
    in_box = {name: {b: f"{name}_in_box_{b}" for b in range(1, n_boxes + 1)} for name in balls}
    for name in balls:
        for flag in in_box[name].values():
            solver.addVariable(flag, 0, 1)

        # Each ball is in exactly one box.
        solver.addConstraint([(1, flag) for flag in in_box[name].values()], True, 1, True, 1)
        # The box of a ball is the number of that box.
        solver.addConstraint([(b, in_box[name][b]) for b in range(1, n_boxes + 1)] + [(-1, name)],
                             True, 0, True, 0)

    # For every x + y = z, with z at most n_balls, the balls x, y and z do not all lie in one box.
    for x in range(1, n_balls):
        for y in range(1, n_balls - x + 1):
            z = x + y
            for box in range(1, n_boxes + 1):
                solver.addConstraint([(1, in_box[balls[x - 1]][box]),
                                      (1, in_box[balls[y - 1]][box]),
                                      (1, in_box[balls[z - 1]][box])], False, 0, True, 2)

    return solver, {"balls": balls}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

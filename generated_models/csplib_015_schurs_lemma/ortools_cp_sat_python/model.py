# csplib_015_schurs_lemma: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_015_schurs_lemma.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_015_schurs_lemma.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_015_schurs_lemma.py csplib_015_schurs_lemma.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Put n balls labelled 1, ..., n into c boxes so that for any triple of balls
    (x, y, z) with x + y = z, not all three are in the same box."""
    n_balls = instance["n"]  # the number of balls, labelled 1, ..., n_balls
    n_boxes = instance["c"]  # the number of boxes, labelled 1, ..., n_boxes

    model = cp_model.CpModel()

    # balls[i] is the box that ball i+1 is put in
    balls = [model.new_int_var(1, n_boxes, f"balls_{i}") for i in range(n_balls)]

    # For every triple x + y = z with z <= n_balls, the balls x, y and z are not all
    # in the same box.
    for x in range(1, n_balls):
        for y in range(1, n_balls - x + 1):
            z = x + y
            # differ: for each pair among x, y and z, true when the pair is in different boxes.
            differ = []
            for a, b in ((x, y), (x, z), (y, z)):
                d = model.new_bool_var(f"differ_{x}_{y}_{a}_{b}")
                model.add(balls[a - 1] != balls[b - 1]).only_enforce_if(d)
                differ.append(d)
            # At least one of the three pairs is in different boxes.
            model.add_bool_or(differ)

    return model, {"balls": balls}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

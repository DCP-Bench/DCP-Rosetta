# car_selection: a Z3 (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python car_selection.py car_selection.json

import z3


def create_model(instance):
    """Participants are assigned to cars. Each participant is interested in some of the cars
    and gets at most one of them, and each car goes to at most one participant. Maximise the
    number of assignments."""
    # possible[i][j] is 1 when participant i is interested in car j, and 0 otherwise
    possible = instance["possible_assignments"]
    n_participants, n_cars = len(possible), len(possible[0])

    # assigned[i][j] is true when participant i gets car j
    assigned = [[z3.Bool(f"assigned_{i}_{j}") for j in range(n_cars)] for i in range(n_participants)]

    # The rules on the assignments.
    solver = z3.Optimize()

    # A participant only gets a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            if possible[i][j] == 0:
                solver.add(z3.Not(assigned[i][j]))

    # Each participant gets at most one car.
    for i in range(n_participants):
        solver.add(z3.AtMost(*assigned[i], 1))

    # Each car goes to at most one participant.
    for j in range(n_cars):
        solver.add(z3.AtMost(*[assigned[i][j] for i in range(n_participants)], 1))

    # The number of assignments, to maximise.
    n_assignments = z3.Sum([z3.If(a, 1, 0) for row in assigned for a in row])
    solver.maximize(n_assignments)

    return solver, {"assignments": assigned}


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

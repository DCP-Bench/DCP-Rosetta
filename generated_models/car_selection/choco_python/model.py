# car_selection: a Choco-solver (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python car_selection.py car_selection.json

from pychoco.model import Model


def create_model(instance):
    """Participants are matched to cars they are interested in. Each participant gets at most
    one car, and each car goes to at most one participant."""
    possible = instance["possible_assignments"]  # possible[i][j]: 1 when participant i is interested in car j
    n_participants = len(possible)               # the number of participants
    n_cars = len(possible[0]) if n_participants else 0  # the number of cars

    model = Model()

    # assign[i][j] is true when participant i is assigned to car j.
    assign = [[model.boolvar(name=f"a{i}_{j}") for j in range(n_cars)]
              for i in range(n_participants)]

    # A participant is assigned only to a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            model.arithm(assign[i][j], "<=", possible[i][j]).post()

    # Each participant gets at most one car.
    for i in range(n_participants):
        model.sum(assign[i], "<=", 1).post()

    # Each car goes to at most one participant.
    for j in range(n_cars):
        model.sum([assign[i][j] for i in range(n_participants)], "<=", 1).post()

    # All participant-car pairs, to count the assignments made.
    pairs = [assign[i][j] for i in range(n_participants) for j in range(n_cars)]
    # The number of assignments made.
    n_matched = model.intvar(0, n_participants * n_cars, name="n_matched")
    model.sum(pairs, "=", n_matched).post()

    # The objective is the number of assignments, as large as possible.
    return model, {"assignments": assign}, {"objective": n_matched, "maximize": True}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

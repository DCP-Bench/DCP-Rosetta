# appointment_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """Schedule people into interview slots based on their free-busy schedules:
    every person gets exactly one slot in which they are free, and every slot
    gets exactly one person."""
    m = instance["m"]     # m[i][j]: whether person i is free in slot j
    n_people = len(m)     # the number of people, which is also the number of slots

    model = Model()

    # x[i][j] is true when person i is assigned to slot j
    x = [[model.boolvar(name=f"x{i}_{j}") for j in range(n_people)] for i in range(n_people)]

    for i in range(n_people):
        # Each person is assigned to exactly one slot.
        model.sum(x[i], "=", 1).post()
        # That slot is one the person is free in.
        model.scalar(x[i], m[i], "=", 1).post()
    # Each slot gets exactly one person.
    for j in range(n_people):
        model.sum([x[i][j] for i in range(n_people)], "=", 1).post()

    return model, {"x": x}, None


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

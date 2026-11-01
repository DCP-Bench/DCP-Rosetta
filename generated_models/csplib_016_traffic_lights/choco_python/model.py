# csplib_016_traffic_lights: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from pychoco.model import Model


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights. Choose a
    state for every light so that each pair of neighbouring roads shows a safe combination
    of states."""
    allowed_tuples = instance["allowed_tuples"]  # the safe (vehicle, pedestrian, next vehicle, next pedestrian) state combinations

    model = Model()

    # vehicle[i] is the state of the vehicle light of road i + 1: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
    vehicle = [model.intvar(0, 3, name=f"V{i + 1}") for i in range(4)]
    # pedestrian[i] is the state of the pedestrian light of road i + 1: 0 = red, 1 = green
    pedestrian = [model.intvar(0, 1, name=f"P{i + 1}") for i in range(4)]

    # Each road and the next one show a safe combination. The roads go round the junction,
    # so road 4 is followed by road 1.
    for i in range(4):
        nxt = (i + 1) % 4
        model.table([vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]], allowed_tuples).post()

    return model, {"lights": vehicle + pedestrian}, None


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

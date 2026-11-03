# csplib_016_traffic_lights: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights.
    Choose a state for every light so that each pair of neighbouring roads shows a
    safe combination of states."""
    # allowed_tuples: the combinations of light states that are safe for two neighbouring roads
    allowed_tuples = instance["allowed_tuples"]

    model = cp_model.CpModel()

    # vehicle[i] is the state of the vehicle light of road i+1:
    # 0=red, 1=red-yellow, 2=green, 3=yellow
    vehicle = [model.new_int_var(0, 3, f"V{i + 1}") for i in range(4)]
    # pedestrian[i] is the state of the pedestrian light of road i+1: 0=red, 1=green
    pedestrian = [model.new_int_var(0, 1, f"P{i + 1}") for i in range(4)]

    # Each road, together with the next one, shows a safe combination. The roads go
    # round the junction, so road 4 is followed by road 1.
    for i in range(4):
        nxt = (i + 1) % 4
        model.add_allowed_assignments(
            [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]], allowed_tuples
        )

    return model, {"lights": vehicle + pedestrian}


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

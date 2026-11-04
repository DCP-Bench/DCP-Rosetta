# csplib_016_traffic_lights: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import z3


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights. Choose a state
    for every light so that each pair of neighbouring roads shows a safe combination of
    states."""
    # allowed_tuples: the safe combinations of states (vehicle light i, pedestrian light i,
    # vehicle light i + 1, pedestrian light i + 1) for two neighbouring roads
    allowed_tuples = instance["allowed_tuples"]

    # V[i] is the state of the vehicle light of road i + 1: 0 red, 1 red-yellow, 2 green, 3 yellow
    vehicle = [z3.Int(f"V{i + 1}") for i in range(4)]
    # P[i] is the state of the pedestrian light of road i + 1: 0 red, 1 green
    pedestrian = [z3.Int(f"P{i + 1}") for i in range(4)]

    solver = z3.Solver()

    # Every vehicle light is in one of its four states.
    solver.add([z3.And(v >= 0, v <= 3) for v in vehicle])
    # Every pedestrian light is in one of its two states.
    solver.add([z3.And(p >= 0, p <= 1) for p in pedestrian])

    # Each road, together with the next one, shows a safe combination. The roads go round
    # the junction, so road 4 is followed by road 1.
    for i in range(4):
        nxt = (i + 1) % 4
        lights = [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]]
        solver.add(z3.Or([z3.And([light == value for light, value in zip(lights, row)])
                          for row in allowed_tuples]))

    return solver, {"lights": vehicle + pedestrian}


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

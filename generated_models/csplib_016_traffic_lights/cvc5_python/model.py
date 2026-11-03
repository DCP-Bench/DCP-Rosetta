# csplib_016_traffic_lights: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import cvc5.pythonic as c5


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights.
    Choose a state for every light so that each pair of neighbouring roads shows a
    safe combination of states."""
    allowed_tuples = instance["allowed_tuples"]  # the safe (V_i, P_i, V_{i+1}, P_{i+1}) combinations of light states

    n_roads = 4  # the junction has four roads

    # vehicle[i] is the state of the vehicle light of road i+1:
    # 0=red, 1=red-yellow, 2=green, 3=yellow
    vehicle = [c5.Int(f"vehicle_{i}") for i in range(n_roads)]
    # pedestrian[i] is the state of the pedestrian light of road i+1: 0=red, 1=green
    pedestrian = [c5.Int(f"pedestrian_{i}") for i in range(n_roads)]
    # the rules that the light states must satisfy
    solver = c5.Solver()

    # Every vehicle light is in one of its four states, and every pedestrian light in one of its two.
    for i in range(n_roads):
        solver.add(vehicle[i] >= 0, vehicle[i] <= 3, pedestrian[i] >= 0, pedestrian[i] <= 1)

    # Each road, together with the next one, shows a safe combination. The roads go
    # round the junction, so road 4 is followed by road 1.
    for i in range(n_roads):
        nxt = (i + 1) % n_roads
        solver.add(c5.Or([
            c5.And(vehicle[i] == a, pedestrian[i] == b, vehicle[nxt] == c, pedestrian[nxt] == d)
            for a, b, c, d in allowed_tuples
        ]))

    lights = vehicle + pedestrian  # all eight lights
    return solver, {"lights": lights}


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

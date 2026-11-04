# csplib_016_traffic_lights: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from exact import Exact


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights. Choose a
    state for every light so that each road and the next one show a safe combination of
    states."""
    # allowed_tuples[k] is a safe combination (V_i, P_i, V_{i+1}, P_{i+1}) of light states
    # for two neighbouring roads
    allowed_tuples = instance["allowed_tuples"]
    n_roads = 4  # the four roads of the junction, each with a vehicle light and a pedestrian light

    solver = Exact()

    # Exact identifies its variables by name.
    # vehicle[i] is the state of the vehicle light of road i + 1: 0 red, 1 red-yellow, 2 green, 3 yellow
    vehicle = [f"V{i + 1}" for i in range(n_roads)]
    for name in vehicle:
        solver.addVariable(name, 0, 3)
    # pedestrian[i] is the state of the pedestrian light of road i + 1: 0 red, 1 green
    pedestrian = [f"P{i + 1}" for i in range(n_roads)]
    for name in pedestrian:
        solver.addVariable(name, 0, 1)

    # Each road and the next one (road 4 is followed by road 1) show one safe combination.
    for i in range(n_roads):
        next_road = (i + 1) % n_roads
        lights = [vehicle[i], pedestrian[i], vehicle[next_road], pedestrian[next_road]]
        # chosen[k] is 1 when the pair of roads shows safe combination k, and 0 when not
        chosen = [f"road{i}_uses_tuple{k}" for k in range(len(allowed_tuples))]
        for name in chosen:
            solver.addVariable(name, 0, 1)

        # The pair shows exactly one safe combination.
        solver.addConstraint([(1, name) for name in chosen], True, 1, True, 1)
        # Each of the four lights is in the state that the chosen combination gives it.
        for position, light in enumerate(lights):
            solver.addConstraint([(1, light)] + [(-allowed_tuples[k][position], chosen[k])
                                                 for k in range(len(allowed_tuples))
                                                 if allowed_tuples[k][position] != 0],
                                 True, 0, True, 0)

    return solver, {"lights": vehicle + pedestrian}


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

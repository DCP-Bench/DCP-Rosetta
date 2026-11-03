# csplib_016_traffic_lights: a CPMpy model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import cpmpy as cp


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights.
    Choose a state for every light so that each pair of neighbouring roads shows a
    safe combination of states."""
    # allowed_tuples: the safe combinations (V_i, P_i, V_{i+1}, P_{i+1}) of light
    # states for two neighbouring roads
    allowed_tuples = instance["allowed_tuples"]

    # vehicle[i] is the state of the vehicle light of road i+1:
    # 0=red, 1=red-yellow, 2=green, 3=yellow
    vehicle = cp.intvar(0, 3, shape=4, name="vehicle")
    # pedestrian[i] is the state of the pedestrian light of road i+1: 0=red, 1=green
    pedestrian = cp.intvar(0, 1, shape=4, name="pedestrian")

    model = cp.Model()
    # Each road, together with the next one, shows a safe combination. The roads
    # go round the junction, so road 4 is followed by road 1.
    for i in range(4):
        nxt = (i + 1) % 4
        model.add(cp.Table([vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]], allowed_tuples))

    # All eight lights in the order V1..V4, P1..P4
    lights = cp.cpm_array(list(vehicle) + list(pedestrian))

    return model, {"lights": lights}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

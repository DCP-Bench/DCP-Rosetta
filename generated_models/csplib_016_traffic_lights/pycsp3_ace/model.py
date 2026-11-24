# csplib_016_traffic_lights: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from pycsp3 import *


def create_model(instance):
    """Four-way traffic junction with eight traffic lights. Four lights (V1 to V4)
    are for vehicles, and four (P1 to P4) are for pedestrians. The lights have
    different states. Only the combinations (V_i, P_i, V_{i+1}, P_{i+1}) listed as
    safe for intersecting roads are allowed, for i = 1 to 4, with V_5 = V_1 and
    P_5 = P_1; every other combination is disallowed to prevent accidents.
    Vehicle light states: 0 = red, 1 = red-yellow, 2 = green, 3 = yellow.
    Pedestrian light states: 0 = red, 1 = green."""
    allowed_tuples = instance["allowed_tuples"]  # the safe (V_i, P_i, V_{i+1}, P_{i+1}) combinations

    n_roads = 4  # four vehicle lights V1 to V4 and four pedestrian lights P1 to P4
    n_vehicle_states = 4  # vehicle states 0 to 3
    n_pedestrian_states = 2  # pedestrian states 0 and 1

    # lights[k] is the state of light k: lights[0] to lights[3] are V1 to V4, lights[4] to lights[7] are P1 to P4
    lights = VarArray(
        size=2 * n_roads,
        dom=lambda k: range(n_vehicle_states) if k < n_roads else range(n_pedestrian_states),
    )
    vehicle = lights[:n_roads]  # V1 to V4
    pedestrian = lights[n_roads:]  # P1 to P4

    satisfy(
        # for each road i, the states (V_i, P_i, V_{i+1}, P_{i+1}) form a safe combination; the index
        # (i + 1) % n_roads sends road 4 back to road 1, as V_5 = V_1 and P_5 = P_1
        Table(
            scope=[vehicle[i], pedestrian[i], vehicle[(i + 1) % n_roads], pedestrian[(i + 1) % n_roads]],
            supports=allowed_tuples,
        )
        for i in range(n_roads)
    )

    return {"lights": lights}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

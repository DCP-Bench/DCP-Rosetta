# csplib_016_traffic_lights: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

from hermax.model import Model


def create_model(instance):
    """Four-way traffic junction: four vehicle lights V1..V4 and four pedestrian lights
    P1..P4. Choose a state for every light so that each pair of neighbouring roads
    (road i and road i+1, with road 4 followed by road 1) shows one of the safe
    combinations; every other combination is forbidden. This is a satisfaction problem."""
    # allowed_tuples[k]: a safe combination (V_i, P_i, V_{i+1}, P_{i+1}) for neighbouring roads
    allowed_tuples = instance["allowed_tuples"]

    m = Model()

    # vehicle[i] is the state of vehicle light V(i+1): 0 = red, 1 = red-yellow, 2 = green, 3 = yellow
    vehicle = m.int_vector("vehicle", 4, 0, 3)
    # pedestrian[i] is the state of pedestrian light P(i+1): 0 = red, 1 = green
    pedestrian = m.int_vector("pedestrian", 4, 0, 1)

    # Every pair of neighbouring roads shows a safe combination: the four lights
    # (V_i, P_i, V_{i+1}, P_{i+1}) must be one of the allowed tuples.
    for i in range(4):
        nxt = (i + 1) % 4
        m &= m.table(
            [vehicle[i], pedestrian[i], vehicle[nxt], pedestrian[nxt]],
            allowed=allowed_tuples,
        )

    # The answer lists the lights in the order V1, V2, V3, V4, P1, P2, P3, P4.
    lights = [vehicle[i] for i in range(4)] + [pedestrian[i] for i in range(4)]
    return m, {"lights": lights}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

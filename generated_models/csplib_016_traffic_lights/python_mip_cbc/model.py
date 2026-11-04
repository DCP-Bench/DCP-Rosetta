# csplib_016_traffic_lights: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import mip


def create_model(instance):
    """A four-way junction has four vehicle lights and four pedestrian lights.
    Choose a state for every light so that each pair of neighbouring roads shows a
    safe combination of states."""
    # allowed_tuples[k]: the k-th safe combination (V_i, P_i, V_{i+1}, P_{i+1}) of light
    # states for two neighbouring roads
    allowed_tuples = instance["allowed_tuples"]
    n_safe = len(allowed_tuples)  # the number of safe combinations

    model = mip.Model(solver_name="CBC")

    # vehicle[i] is the state of the vehicle light of road i+1:
    # 0=red, 1=red-yellow, 2=green, 3=yellow
    vehicle = [model.add_var(f"V{i + 1}", lb=0, ub=3, var_type=mip.INTEGER) for i in range(4)]
    # pedestrian[i] is the state of the pedestrian light of road i+1: 0=red, 1=green
    pedestrian = [model.add_var(f"P{i + 1}", lb=0, ub=1, var_type=mip.INTEGER) for i in range(4)]

    # Each road, together with the next one, shows a safe combination. The roads go round
    # the junction, so road 4 is followed by road 1.
    for i in range(4):
        nxt = (i + 1) % 4

        # choice[k] is 1 when this pair of roads shows the k-th safe combination
        choice = [model.add_var(f"z_{i}_{k}", var_type=mip.BINARY) for k in range(n_safe)]
        model += mip.xsum(choice) == 1

        # The four lights of the pair take the values of the chosen combination.
        model += vehicle[i] == mip.xsum(allowed_tuples[k][0] * choice[k] for k in range(n_safe))
        model += pedestrian[i] == mip.xsum(allowed_tuples[k][1] * choice[k] for k in range(n_safe))
        model += vehicle[nxt] == mip.xsum(allowed_tuples[k][2] * choice[k] for k in range(n_safe))
        model += pedestrian[nxt] == mip.xsum(allowed_tuples[k][3] * choice[k] for k in range(n_safe))

    # All eight lights, V1..V4 then P1..P4.
    lights = vehicle + pedestrian

    return model, {"lights": lights}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

# csplib_016_traffic_lights: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_016_traffic_lights.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_016_traffic_lights.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_016_traffic_lights.py csplib_016_traffic_lights.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Traffic lights at a four-way junction: four vehicle lights (V1 to V4) and four
    pedestrian lights (P1 to P4), each in one of its states. The junction has four
    pairs of intersecting roads, and for each pair i = 1..4 the lights (V_i, P_i,
    V_i+1, P_i+1) must form one of the safe combinations listed in the instance, where
    V_5 = V_1 and P_5 = P_1. Find a state for every light; the states are returned as
    outputs["lights"] = [V1, V2, V3, V4, P1, P2, P3, P4]."""
    # allowed[k] = [V_i, P_i, V_i+1, P_i+1]: the k-th safe combination of light states
    allowed = np.array(instance["allowed_tuples"])
    n_allowed = len(allowed)  # how many safe combinations the instance lists

    model = Model("traffic_lights")

    # state[i, 0] is the vehicle light and state[i, 1] the pedestrian light at position i,
    # with positions 0..3 standing for lights 1..4. Vehicle states run 0..3 (red,
    # red-yellow, green, yellow) and pedestrian states 0..1 (red, green), as the
    # problem statement gives them.
    state = model.addMatrixVar((4, 2), vtype="I", lb=0, ub=[[3, 1]] * 4, name="state")

    # chosen[i, k] is 1 when road pair i shows the k-th safe combination. Each road pair
    # shows exactly one safe combination.
    chosen = model.addMatrixVar((4, n_allowed), vtype="B", name="chosen")
    model.addMatrixCons(chosen.sum(axis=1) == 1)

    # Each road pair i reads its current lights from the first two entries of its chosen
    # combination and its next lights from the last two. The next lights of pair i are
    # the lights at position i+1. np.roll(..., -1) moves each row up one place and the
    # last row wraps to the first, so the last pair's next lights are light 1's (V_5 = V_1
    # and P_5 = P_1). PySCIPOpt has no table constraint, so the choice among the safe
    # combinations is written with the one-hot binaries above.
    model.addMatrixCons(chosen @ allowed[:, :2] == state)  # current lights of each road pair
    model.addMatrixCons(
        chosen @ allowed[:, 2:] == np.roll(state, -1, axis=0)  # next lights of each road pair
    )

    # The problem asks for any valid assignment, so the model has no objective.

    # The eight light states in the output order: all vehicle lights, then all pedestrian lights.
    lights = state.T.flatten()
    return model, {"lights": lights}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

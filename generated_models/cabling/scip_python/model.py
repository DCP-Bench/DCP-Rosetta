# cabling: a SCIP (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python cabling.py cabling.json

import numpy as np
from pyscipopt import Model, quicksum


def create_model(instance):
    """Devices are mounted one above another in a rack cabinet, one device per
    1U slot, and some pairs of devices are joined by cables. A cable's length is
    the distance between the slots of the two devices it joins. Choose the order
    of the devices so that the sum of all cable lengths is as short as possible."""
    n = instance["n"]                  # the number of devices, which is also the number of slots
    devices = instance["devices"]      # devices[i]: the name of device i
    cables = instance["cable_struct"]  # rows [a, b, k]: k cables join device a and device b
    index = {name: i for i, name in enumerate(devices)}  # device name -> its index in devices

    model = Model("cabling")

    # x[d, s] is 1 when device d sits in slot s, and 0 when not. The statement
    # orders all the devices, so the rack has one slot per device (n slots, numbered
    # 0 to n-1; the numbering only sets an origin, since costs use differences).
    x = model.addMatrixVar((n, n), vtype="B", name="x")

    # Each device sits in exactly one slot.
    model.addMatrixCons(x.sum(axis=1) == 1)
    # Each slot holds exactly one device.
    model.addMatrixCons(x.sum(axis=0) == 1)

    # slot[d] is the slot number of device d: the expression sum over s of s * x[d, s].
    slot = x @ np.arange(n)

    # length[j] is the distance in slots between the two devices of cable row j,
    # taking one cable's length to be the number of slots between its ends. Only the
    # two lower bounds are posted: the objective pushes length down, so at the
    # optimum length equals |slot[a] - slot[b]|. Its upper bound n - 1 holds because
    # every slot number lies between 0 and n - 1.
    length = []
    for a, b, _ in cables:
        i, j = index[a], index[b]
        d = model.addVar(vtype="I", lb=0, ub=n - 1, name=f"length_{a}{b}")
        model.addCons(d >= slot[i] - slot[j])
        model.addCons(d >= slot[j] - slot[i])
        length.append(d)

    # final_sum is the total length of all cables: each cable of row j contributes
    # its length, and row j has k cables. Its upper bound is (n - 1) times the total
    # number of cables, since no cable is longer than n - 1 slots.
    total_cables = sum(k for _, _, k in cables)
    final_sum = model.addVar(vtype="I", lb=0, ub=(n - 1) * total_cables, name="final_sum")
    model.addCons(final_sum == quicksum(k * d for (_, _, k), d in zip(cables, length)))

    # Minimise the sum of all cable lengths.
    model.setObjective(final_sum, "minimize")

    return model, {"final_sum": final_sum}


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

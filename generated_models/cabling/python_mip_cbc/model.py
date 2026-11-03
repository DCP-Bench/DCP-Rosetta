# cabling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python cabling.py cabling.json

import mip


def create_model(instance):
    """Devices in a rack cabinet are placed one above another, one device per place. Cables
    join pairs of devices, and a cable is as long as the distance between their places.
    Order the devices so that the total cable length is as short as possible."""
    n_devices = instance["n"]          # the number of devices, and of places in the rack
    devices = instance["devices"]      # the names of the devices
    cables = instance["cable_struct"]  # each entry [a, b, count]: count cables join devices a and b
    max_dist = n_devices - 1           # the largest distance between two places

    index = {name: i for i, name in enumerate(devices)}

    model = mip.Model(solver_name="CBC")

    # p[i][k] is 1 when device i sits at place k in the rack, and 0 when not
    p = [
        [model.add_var(f"p_{i}_{k}", var_type=mip.BINARY) for k in range(n_devices)]
        for i in range(n_devices)
    ]

    # Each device sits in exactly one place.
    for i in range(n_devices):
        model += mip.xsum(p[i]) == 1

    # Each place holds exactly one device.
    for k in range(n_devices):
        model += mip.xsum(p[i][k] for i in range(n_devices)) == 1

    # pos[i] is the place of device i, counted from 0
    pos = [model.add_var(f"pos_{i}", lb=0, ub=max_dist, var_type=mip.INTEGER) for i in range(n_devices)]
    # The place of each device is the place it sits at.
    for i in range(n_devices):
        model += pos[i] == mip.xsum(k * p[i][k] for k in range(n_devices))

    # length_terms[c] is the total length of the cables in row c
    length_terms = []
    # the longest the total cable length can be: every cable at the largest distance
    total_ub = 0
    for c, (a, b, count) in enumerate(cables):
        # d[c] is the distance between the two devices of row c. Both lower bounds are needed
        # because the total length is minimised, so d takes the size of the difference.
        d = model.add_var(f"d_{c}", lb=0, ub=max_dist, var_type=mip.INTEGER)
        model += d >= pos[index[a]] - pos[index[b]]
        model += d >= pos[index[b]] - pos[index[a]]
        length_terms.append(count * d)
        total_ub += count * max_dist

    # final_sum is the sum of the cable lengths of all rows.
    final_sum = model.add_var("final_sum", lb=0, ub=total_ub, var_type=mip.INTEGER)
    model += final_sum == mip.xsum(length_terms)

    # Make the total cable length as short as possible.
    model.objective = final_sum

    return model, {"final_sum": final_sum}


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

# cabling: a PuLP (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python cabling.py cabling.json

import pulp


def create_model(instance):
    """Devices are placed one above another in a rack, one per slot, and some are joined by
    one or several cables. Order the devices so that the sum of all cable lengths is as short
    as possible."""
    n_devices = instance["n"]          # the number of devices, and of rack slots
    devices = instance["devices"]      # devices[i]: the name of device i
    cables = instance["cable_struct"]  # each entry [a, b, count]: count cables join devices a and b

    # links[k] is the pair of devices joined by link k, as device numbers, and its number of cables
    links = [(devices.index(a), devices.index(b), count) for a, b, count in cables]

    problem = pulp.LpProblem("cabling", pulp.LpMinimize)

    # in_slot[d][p] is 1 when device d sits in slot p, and 0 when not.
    in_slot = [[pulp.LpVariable(f"in_slot_{d}_{p}", cat="Binary") for p in range(n_devices)]
               for d in range(n_devices)]
    # x[d] is the slot of device d, numbered from 0.
    x = [pulp.LpVariable(f"x_{d}", 0, n_devices - 1, cat="Integer") for d in range(n_devices)]

    # Each device sits in exactly one slot.
    for d in range(n_devices):
        problem += pulp.lpSum(in_slot[d]) == 1
    # Each slot holds exactly one device.
    for p in range(n_devices):
        problem += pulp.lpSum(in_slot[d][p] for d in range(n_devices)) == 1

    # The slot of device d is the slot it sits in.
    for d in range(n_devices):
        problem += x[d] == pulp.lpSum(p * in_slot[d][p] for p in range(n_devices))

    # Turning the rack upside down keeps every cable length, so device 0 can be taken
    # in the lower half of the rack.
    if n_devices > 0:
        problem += 2 * x[0] <= n_devices - 1

    # length[k] is the number of slots between the two devices of link k.
    length = [pulp.LpVariable(f"length_{k}", 0, n_devices - 1) for k in range(len(links))]
    # The gap between two slots is the difference of their numbers, in either direction.
    for k, (a, b, _) in enumerate(links):
        problem += length[k] >= x[a] - x[b]
        problem += length[k] >= x[b] - x[a]

    # final_sum is the total length of all cables. No cable is longer than n_devices - 1 slots.
    final_sum = pulp.LpVariable("final_sum", 0,
                                (n_devices - 1) * sum(count for _, _, count in links),
                                cat="Integer")
    # Each link contributes its length once for every cable in it.
    problem += final_sum == pulp.lpSum(count * length[k] for k, (_, _, count) in enumerate(links))

    # Make the total cable length as short as possible.
    problem += final_sum

    return problem, {"final_sum": final_sum}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

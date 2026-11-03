# cabling: a CPMpy model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python cabling.py cabling.json

import cpmpy as cp


def create_model(instance):
    """Devices are placed one above another in a rack, one per slot, and some are joined by
    one or several cables. Order the devices so that the sum of all cable lengths is as short
    as possible."""
    n = instance["n"]                  # the number of devices, and of rack slots
    devices = instance["devices"]      # devices[i]: the name of device i
    cables = instance["cable_struct"]  # each entry [a, b, count]: count cables join devices a and b

    # Cables name devices by their name; turn each into the index of the device.
    links = [(devices.index(a), devices.index(b), count) for a, b, count in cables]

    # x[d] is the rack slot of device d
    x = cp.intvar(0, n - 1, shape=n, name="x")
    # t[k] is the total length of the cables of link k
    t = cp.intvar(1, n * n, shape=len(links), name="t")
    # final_sum is the sum of all cable lengths. Its upper bound takes the largest
    # distance between two slots (below n), for every cable of every link.
    final_sum = cp.intvar(0, n * sum(count for _, _, count in links), name="final_sum")

    model = cp.Model()
    # Every device gets its own slot in the rack.
    model.add(cp.AllDifferent(x))
    # A cable is as long as the distance between the slots of its two devices,
    # so the cables of a link have that length times their number.
    for k, (a, b, count) in enumerate(links):
        model.add(t[k] == cp.abs(x[a] - x[b]) * count)
    # The sum of all cable lengths is the sum over all links.
    model.add(final_sum == cp.sum(t))

    # Make the sum of all cable lengths as short as possible.
    model.minimize(final_sum)

    return model, {"final_sum": final_sum}


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

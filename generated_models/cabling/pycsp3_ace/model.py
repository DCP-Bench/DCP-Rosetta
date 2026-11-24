# cabling: a PyCSP3 model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python cabling.py cabling.json

from pycsp3 import *


def create_model(instance):
    """Devices in a rack, one per 1U position, must be cabled together. Each device takes one
    position, and neighbouring positions are one unit apart. A cable between two devices is as
    long as the distance between their positions, so k cables between two devices cost k times
    that distance. Place the devices so that the sum of all cable lengths is as short as
    possible, and find that sum."""
    devices = instance["devices"]            # the device names; devices[i] is device i
    n_devices = instance["n"]                # the number of devices
    cable_struct = instance["cable_struct"]  # [a, b, k]: k cables connect devices a and b

    # Each cable entry as (index of device a, index of device b, number of cables).
    cables = [(devices.index(a), devices.index(b), k) for a, b, k in cable_struct]
    total_cables = sum(k for _, _, k in cables)

    # position[i] is the rack position of device i. The n_devices devices fill the n_devices
    # positions 0 to n_devices - 1 in some order.
    position = VarArray(size=n_devices, dom=range(n_devices))
    # Each device takes a position of its own.
    satisfy(AllDifferent(position))

    # The total cable length: each cable is as long as the distance between its two devices.
    # No cable is longer than n_devices - 1, so the total is at most that times the cable count.
    final_sum = Var(dom=range(total_cables * (n_devices - 1) + 1))
    satisfy(final_sum == Sum(k * abs(position[a] - position[b]) for a, b, k in cables))

    # Place the devices so that the total cable length is as short as possible.
    minimize(final_sum)

    return {"final_sum": final_sum}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

# cabling: a hermax (Python) model from DCP Rosetta.
# Download the `cabling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cabling.html
# Then run it on the first instance (after `pip install hermax`):
#   python cabling.py cabling.json
from hermax.model import Model, sum_expr


def create_model(instance):
    """Place each device in its own slot of a rack, one device per slot, so that the total
    length of the cables is as small as possible. A cable group joining two devices costs
    the number of cables in it times the distance between their slots."""
    n = instance["n"]                  # number of devices, which is also the number of rack slots
    devices = instance["devices"]      # devices[i]: the name of device i
    cables = instance["cable_struct"]  # cables[k]: [device a, device b, number of cables between them]

    index = {name: i for i, name in enumerate(devices)}  # index[name]: the position of a device by its name

    m = Model()

    # slot[d] is the rack slot of device d (0 is the bottom slot)
    slot = m.int_vector("slot", n, 0, n - 1)
    # Every device sits in its own slot, so no two devices share a slot.
    m &= slot.all_different()

    lengths = []  # lengths[k]: the distance between the slots of the two devices of cable group k
    for k, (a, b, count) in enumerate(cables):
        ia, ib = index[a], index[b]
        length = m.int(f"length_{k}", 1, n - 1)  # distinct slots are at least 1 apart
        # Minimisation makes length equal to |slot[a] - slot[b]|: one of these two bounds is tight.
        m &= (length >= slot[ib] - slot[ia])
        m &= (length >= slot[ia] - slot[ib])
        lengths.append(length)

    # The total cable length: each cable group contributes its cable count times its length.
    total_length = sum_expr(count * lengths[k] for k, (_, _, count) in enumerate(cables))

    # Minimise the total cable length.
    m.obj += total_length

    return m, {"final_sum": total_length}


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

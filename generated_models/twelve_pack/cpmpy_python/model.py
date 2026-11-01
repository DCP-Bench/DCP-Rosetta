# twelve_pack: a CPMpy model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python twelve_pack.py twelve_pack.json

import cpmpy as cp


def create_model(instance):
    """Given a target number of items, find the combination of packs of different sizes
    that meets or exceeds the target with as few items as possible."""
    target = instance["target"]  # the number of items needed
    packs = instance["packs"]    # packs[i]: the number of items in a pack of kind i

    # A pack count never needs to exceed the target: that many packs of any kind already meet it.
    # Twice the target leaves slack.
    ceiling = target * 2

    # counts[i] is how many packs of kind i are bought
    counts = cp.intvar(0, ceiling, shape=len(packs), name="counts")
    # total is the number of items bought. Its upper bound 2 * target * (number of pack kinds) is
    # not the largest possible sum, but the best total is less than target + the largest pack,
    # which stays below it.
    total = cp.intvar(0, ceiling * len(packs), name="total")

    model = cp.Model()

    # The total is the number of items in all the packs bought.
    model.add(total == cp.sum(counts * packs))

    # The total meets or exceeds the target.
    model.add(total >= target)

    # Buy as few items as possible, so the total is as close to the target as possible.
    model.minimize(total)

    return model, {"counts": counts}


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

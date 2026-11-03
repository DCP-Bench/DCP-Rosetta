# bales_of_hay: a CPMpy model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python bales_of_hay.py bales_of_hay.json

import itertools

import cpmpy as cp


def create_model(instance):
    """Bales of hay were weighed in all possible combinations of two, and the
    weights of these pairs were written down in order. Find the weight of each bale."""
    n = instance["n"]                # the number of bales
    weights = instance["weights"]    # the weight of each pair of bales, in numerical order

    # bales[i] is the weight of bale i; no bale outweighs the heaviest pair it is in
    bales = cp.intvar(0, max(weights), shape=n, name="bales")

    model = cp.Model()
    # Each written-down weight is the weight of some pair of distinct bales.
    for weight in weights:
        model.add(cp.any([bales[i] + bales[j] == weight
                         for i, j in itertools.combinations(range(n), 2)]))

    return model, {"bales": bales}


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

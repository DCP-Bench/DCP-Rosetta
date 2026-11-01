# among: a CPMpy model from DCP Rosetta.
# Download the `among.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/among.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python among.py among.json

import cpmpy as cp


def create_model(instance):
    """Exactly m of the values in x take one of the values in v. Every value in x
    is at least 0 and at most 7."""
    n = instance["n"]  # the number of values in x
    m = instance["m"]  # how many values in x must take a value from v
    v = instance["v"]  # the values that are counted

    # x[i] is the ith value; the problem allows 0 to 7
    x = cp.intvar(0, 7, shape=n, name="x")

    model = cp.Model()

    # Exactly m of the values in x take one of the values in v.
    model.add(cp.sum([cp.sum(x == value) for value in v]) == m)

    return model, {"x": x}


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

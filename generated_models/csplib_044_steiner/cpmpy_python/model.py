# csplib_044_steiner: a CPMpy model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_044_steiner.py csplib_044_steiner.json

import cpmpy as cp


def create_model(instance):
    """Find n * (n - 1) / 6 triples of distinct elements of {1, ..., n} such that any two
    triples have at most one element in common (n is 1 or 3 modulo 6)."""
    n = instance["n"]          # the number of elements
    n_sets = n * (n - 1) // 6  # the number of triples required

    # sets[i, j] is true when element j belongs to triple i
    sets = cp.boolvar(shape=(n_sets, n), name="sets")

    model = cp.Model()

    # Each triple has three elements.
    for i in range(n_sets):
        model.add(cp.sum(sets[i]) == 3)

    # Any two triples have at most one element in common.
    for i in range(n_sets):
        for k in range(i + 1, n_sets):
            model.add(cp.sum(sets[i] & sets[k]) <= 1)

    return model, {"sets": sets}


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

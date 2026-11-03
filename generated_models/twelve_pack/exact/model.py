# twelve_pack: an Exact (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python twelve_pack.py twelve_pack.json

from exact import Exact


def create_model(instance):
    """Given a number of items needed, buy whole packs of different sizes so that the
    items bought meet or exceed the number needed, using as few items as possible."""
    target = instance["target"]  # the number of items needed
    packs = instance["packs"]    # packs[i]: the number of items in a pack of kind i
    n_kinds = len(packs)         # the number of pack kinds

    ceiling = target * 2  # the most packs of one kind that can be bought

    solver = Exact()

    # Exact identifies its variables by name.
    # counts[i] is the number of packs of kind i that are bought
    counts = [f"c{i}" for i in range(n_kinds)]
    for name in counts:
        solver.addVariable(name, 0, ceiling)

    # total is the number of items bought, at least the number needed
    solver.addVariable("total", target, ceiling * n_kinds)
    # The items in all the packs bought make up the total.
    solver.addConstraint(list(zip(packs, counts)) + [(-1, "total")], True, 0, True, 0)

    # Buy as few items as possible.
    solver.setObjective([(1, "total")], minimize=True)

    return solver, {"counts": counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

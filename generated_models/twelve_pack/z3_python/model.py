# twelve_pack: a Z3 (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python twelve_pack.py twelve_pack.json

import z3


def create_model(instance):
    """Given a target number of items, find the combination of packs of different sizes
    that meets or exceeds the target with as few items as possible."""
    target = instance["target"]  # the number of items needed
    packs = instance["packs"]    # packs[i]: the number of items in a pack of kind i

    # Each count stays at or below twice the target.
    ceiling = target * 2

    # counts[i] is how many packs of kind i are bought
    counts = [z3.Int(f"n_{i}") for i in range(len(packs))]
    # total is the number of items bought
    total = z3.Int("total")

    solver = z3.Optimize()

    # Each count is between 0 and the ceiling.
    solver.add([c >= 0 for c in counts] + [c <= ceiling for c in counts])

    # The number of items bought stays within its bound.
    solver.add(total >= 0, total <= ceiling * len(packs))

    # The total is the number of items in all the packs bought.
    solver.add(total == z3.Sum([c * p for c, p in zip(counts, packs)]))

    # The items bought meet or exceed the target.
    solver.add(total >= target)

    # Buy as few items as possible.
    solver.minimize(total)

    return solver, {"counts": counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

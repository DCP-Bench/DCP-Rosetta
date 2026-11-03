# twelve_pack: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install ortools`):
#   python twelve_pack.py twelve_pack.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given a target number of items, find the combination of packs of different sizes
    that meets or exceeds the target with as few items as possible."""
    n_needed = instance["target"]  # the number of items needed
    packs = instance["packs"]      # packs[i]: the number of items in a pack of kind i

    # Each count is capped at twice the number of items needed.
    ceiling = n_needed * 2

    model = cp_model.CpModel()

    # counts[i] is how many packs of kind i are bought
    counts = [model.new_int_var(0, ceiling, f"n_{i}") for i in range(len(packs))]
    # The number of items bought
    n_items = model.new_int_var(0, ceiling * len(packs), "n_items")

    # The items bought are the items in all the packs taken.
    model.add(n_items == sum(c * p for c, p in zip(counts, packs)))
    # The items bought meet or exceed the number needed.
    model.add(n_items >= n_needed)

    # Buy as few items as possible.
    model.minimize(n_items)

    return model, {"counts": counts}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

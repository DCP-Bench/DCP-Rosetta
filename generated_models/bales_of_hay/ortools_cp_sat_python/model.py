# bales_of_hay: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install ortools`):
#   python bales_of_hay.py bales_of_hay.json

import itertools

from ortools.sat.python import cp_model

# no bale weighs more than this
HEAVIEST = 50


def create_model(instance):
    """Bales of hay were weighed in every combination of two, and the weights of the
    pairs were written down in numerical order without saying which pair gave which weight.
    Find the weight of each bale."""
    n_bales = instance["n"]        # the number of bales
    weights = instance["weights"]  # the weight of each pair of bales that was written down

    model = cp_model.CpModel()

    # bales[i] is the weight of bale i
    bales = [model.new_int_var(0, HEAVIEST, f"bale_{i}") for i in range(n_bales)]
    # every pair of different bales
    pairs = list(itertools.combinations(range(n_bales), 2))

    # Each written weight is the total weight of some pair of different bales.
    for position, weight in enumerate(weights):
        # picks: which pair of bales gives this weight
        picks = []
        for i, j in pairs:
            pick = model.new_bool_var(f"pick_{position}_{i}_{j}")
            model.add(bales[i] + bales[j] == weight).only_enforce_if(pick)
            picks.append(pick)
        model.add_bool_or(picks)

    return model, {"bales": bales}


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

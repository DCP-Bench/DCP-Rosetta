# bin_packing: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install ortools`):
#   python bin_packing.py bin_packing.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Assign each item to a bin so that the items in each bin weigh no more than the
    bin's capacity."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a bin can hold
    n_bins = instance["num_bins"]    # the number of bins, numbered from 0

    model = cp_model.CpModel()

    # bins[j] is the bin that item j goes into
    bins = [model.new_int_var(0, n_bins - 1, f"bin_{j}") for j in range(len(weights))]
    # in_bin[j][i] is true when item j goes into bin i
    in_bin = [[model.new_bool_var(f"in_{j}_{i}") for i in range(n_bins)]
              for j in range(len(weights))]

    # item j is in bin i exactly when bins[j] is i, and each item is in exactly one bin.
    for j in range(len(weights)):
        for i in range(n_bins):
            model.add(bins[j] == i).only_enforce_if(in_bin[j][i])
            model.add(bins[j] != i).only_enforce_if(~in_bin[j][i])
        model.add_exactly_one(in_bin[j])

    # The items in each bin weigh no more than the capacity.
    for i in range(n_bins):
        model.add(sum(w * in_bin[j][i] for j, w in enumerate(weights)) <= capacity)

    return model, {"bins": bins}


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

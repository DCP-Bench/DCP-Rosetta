# bin_packing: a Choco-solver (Python) model from DCP Rosetta.
# Download the `bin_packing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bin_packing.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python bin_packing.py bin_packing.json

from pychoco.model import Model


def create_model(instance):
    """Bin packing: assign each item to a bin so that the items in each bin weigh no more
    than the bin's capacity."""
    weights = instance["weights"]    # weights[j]: the weight of item j
    capacity = instance["capacity"]  # the most weight a bin can hold
    n_bins = instance["num_bins"]    # the number of bins available

    model = Model()

    # bins[j] is the bin that item j goes into
    bins = [model.intvar(0, n_bins - 1, name=f"bin{j}") for j in range(len(weights))]

    # The items in each bin weigh no more than the capacity.
    for b in range(n_bins):
        # here[j] is true when item j goes into bin b
        here = [model.arithm(bins[j], "=", b).reify() for j in range(len(weights))]
        model.scalar(here, weights, "<=", capacity).post()

    return model, {"bins": bins}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

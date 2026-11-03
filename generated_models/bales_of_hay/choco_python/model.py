# bales_of_hay: a Choco-solver (Python) model from DCP Rosetta.
# Download the `bales_of_hay.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bales_of_hay.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python bales_of_hay.py bales_of_hay.json

from pychoco.model import Model


def create_model(instance):
    """Bales of hay were weighed in every combination of two, and the weights of the
    pairs were written down in numerical order without saying which pair gave which
    weight. Find the weight of each bale."""
    n = instance["n"]              # the number of bales
    weights = instance["weights"]  # the weight of each pair of bales, in numerical order

    # No bale is heavier than the heaviest pair.
    heaviest = max(weights)

    model = Model()

    # bales[i] is the weight of bale i
    bales = [model.intvar(0, heaviest, name=f"bales_{i}") for i in range(n)]

    # every pair of different bales
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]

    # pair_weight[k] is the total weight of the k-th pair
    pair_weight = []
    for i, j in pairs:
        weight = model.intvar(0, heaviest, name=f"pair_weight_{i}_{j}")
        model.arithm(bales[i], "+", bales[j], "=", weight).post()
        pair_weight.append(weight)

    # written_down[k] is the k-th smallest weight that was written down
    written_down = [model.intvar(w, w) for w in sorted(weights)]

    # The pair weights, in numerical order, are the written-down weights.
    model.sort(pair_weight, written_down).post()

    return model, {"bales": bales}, None


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

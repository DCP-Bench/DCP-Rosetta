# twelve_pack: a Choco-solver (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python twelve_pack.py twelve_pack.json

from pychoco.model import Model


def create_model(instance):
    """Given a target number of items, find the closest combination of packs of different
    sizes that meets or exceeds the target."""
    target = instance["target"]  # the number of items wanted
    packs = instance["packs"]    # packs[i]: the number of items in one pack of kind i
    n_kinds = len(packs)         # the number of pack kinds

    max_packs = target * 2       # the most packs of one kind that may be bought

    model = Model()

    # counts[i] is the number of packs of kind i bought
    counts = [model.intvar(0, max_packs, name=f"counts_{i}") for i in range(n_kinds)]
    # total is the number of items bought
    total = model.intvar(0, max_packs * n_kinds, name="total", bounded_domain=True)

    # The items bought are the items in all the packs bought.
    model.scalar(counts, packs, "=", total).post()

    # At least the target number of items is bought.
    model.arithm(total, ">=", target).post()

    # Buy as few items as possible, which is the closest combination that meets the target.
    return model, {"counts": counts}, {"objective": total, "maximize": False}


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

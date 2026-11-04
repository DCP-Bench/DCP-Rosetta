# media_selection: an Exact (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python media_selection.py media_selection.json

from exact import Exact


def create_model(instance):
    """Select advertising media so that every target audience is reached by at least one
    selected medium, at the lowest total campaign cost."""
    target_audiences = instance["target_audiences"]    # the target audiences
    advertising_media = instance["advertising_media"]  # the advertising media
    incidence = instance["incidence_matrix"]           # incidence[t][k]: 1 when medium k reaches audience t
    costs = instance["media_costs"]                    # costs[k]: the cost of medium k
    n_audiences = len(target_audiences)  # the number of target audiences
    n_media = len(advertising_media)     # the number of advertising media

    solver = Exact()

    # Exact identifies its variables by name.
    # is_selected[k] is 1 when medium k is selected, and 0 when not
    is_selected = [f"is_selected_{k}" for k in range(n_media)]
    for name in is_selected:
        solver.addVariable(name, 0, 1)

    # Every audience is reached by at least one selected medium. Reaching it more than once is fine.
    for t in range(n_audiences):
        solver.addConstraint(
            [(incidence[t][k], is_selected[k]) for k in range(n_media) if incidence[t][k]],
            True, 1)

    # min_total_cost is the total cost of the selected media
    solver.addVariable("min_total_cost", 0, sum(costs))
    solver.addConstraint(list(zip(costs, is_selected)) + [(-1, "min_total_cost")],
                         True, 0, True, 0)

    # Spend as little as possible.
    solver.setObjective([(1, "min_total_cost")], minimize=True)

    return solver, {"is_selected": is_selected, "min_total_cost": "min_total_cost"}


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

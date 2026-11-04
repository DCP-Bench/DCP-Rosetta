# media_selection: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install ortools`):
#   python media_selection.py media_selection.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Select advertising media so that every target audience is reached by at least one
    selected medium, at the lowest total campaign cost."""
    target_audiences = instance["target_audiences"]    # the target audiences
    advertising_media = instance["advertising_media"]  # the advertising media
    incidence = instance["incidence_matrix"]           # incidence[t][m]: 1 if medium m reaches audience t
    costs = instance["media_costs"]                    # costs[m]: the cost of medium m
    n_audiences = len(target_audiences)  # the number of target audiences
    n_media = len(advertising_media)     # the number of advertising media

    model = cp_model.CpModel()

    # is_selected[m] is true when medium m is selected
    is_selected = [model.new_bool_var(f"is_selected_{m}") for m in range(n_media)]

    # Every audience is reached by at least one selected medium. Reaching it more than once is fine.
    for t in range(n_audiences):
        model.add(sum(incidence[t][m] * is_selected[m] for m in range(n_media)) >= 1)

    # min_total_cost is the total cost of the selected media
    min_total_cost = sum(costs[m] * is_selected[m] for m in range(n_media))

    # Spend as little as possible.
    model.minimize(min_total_cost)

    return model, {"is_selected": is_selected, "min_total_cost": min_total_cost}


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

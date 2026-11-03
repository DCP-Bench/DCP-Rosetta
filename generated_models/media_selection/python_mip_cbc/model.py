# media_selection: a Python-MIP (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python media_selection.py media_selection.json

import mip


def create_model(instance):
    """Choose which advertising media to buy so that every target audience is reached
    by at least one chosen medium, at the lowest total campaign cost."""
    incidence = instance["incidence_matrix"]  # incidence[i][j] is 1 when medium j reaches audience i, 0 otherwise
    costs = instance["media_costs"]           # costs[j] is the price of buying medium j
    n_media = len(instance["advertising_media"])  # the number of media
    n_audiences = len(instance["target_audiences"])  # the number of audiences to reach

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # is_selected[j] is 1 when medium j is bought, and 0 when not
    is_selected = [model.add_var(f"is_selected_{j}", var_type=mip.BINARY) for j in range(n_media)]

    # min_total_cost is the total campaign cost
    total = model.add_var("min_total_cost", var_type=mip.INTEGER, lb=0, ub=sum(costs))

    # The campaign cost adds up the prices of the bought media.
    model.add_constr(total == mip.xsum(costs[j] * is_selected[j] for j in range(n_media)))

    # Each audience is reached by at least one bought medium. Reaching it more than once is fine.
    for i in range(n_audiences):
        model.add_constr(mip.xsum(incidence[i][j] * is_selected[j] for j in range(n_media)) >= 1)

    # Spend as little as possible.
    model.objective = total

    return model, {"is_selected": is_selected, "min_total_cost": total}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

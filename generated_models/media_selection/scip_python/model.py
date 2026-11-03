# media_selection: a SCIP (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python media_selection.py media_selection.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Choose which advertising media to buy so that every target audience is
    reached by at least one bought medium, at the lowest total campaign cost.
    An audience reached by several bought media is fine."""
    costs = instance["media_costs"]  # costs[j]: the price of buying medium j
    # reach[a][j] is 1 when medium j reaches audience a, and 0 when not;
    # one row per target audience, one column per medium
    reach = np.array(instance["incidence_matrix"])
    n_media = reach.shape[1]

    model = Model("media_selection")

    # is_selected[j] is 1 when medium j is bought, and 0 when not
    is_selected = model.addMatrixVar((n_media,), vtype="B", name="is_selected")

    # Every audience is reached by at least one bought medium: for each audience,
    # the bought media that reach it add up to at least 1.
    model.addMatrixCons((reach @ is_selected) >= 1)

    # The total price of the bought media, which the campaign should minimise.
    total_cost = np.array(costs) @ is_selected
    model.setObjective(total_cost, "minimize")

    return model, {"is_selected": is_selected, "min_total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

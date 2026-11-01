# media_selection: a CPMpy model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python media_selection.py media_selection.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Select advertising media so that every target audience is reached by at least one
    selected medium, at the lowest total campaign cost."""
    incidence = np.array(instance["incidence_matrix"])  # incidence[t, m]: 1 if medium m reaches audience t
    costs = np.array(instance["media_costs"])           # costs[m]: the cost of medium m
    n_media = len(instance["advertising_media"])        # the number of media

    # is_selected[m] is true when medium m is selected
    is_selected = cp.boolvar(shape=n_media, name="is_selected")

    # min_total_cost is the total cost of the selected media
    min_total_cost = cp.intvar(0, int(costs.sum()), name="min_total_cost")

    model = cp.Model()

    # Every audience is reached by at least one selected medium (more than one is fine).
    model.add(incidence @ is_selected >= 1)

    # The total cost is the sum of the costs of the selected media.
    model.add(min_total_cost == cp.sum(is_selected * costs))

    # Spend as little as possible.
    model.minimize(min_total_cost)

    return model, {"is_selected": is_selected, "min_total_cost": min_total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

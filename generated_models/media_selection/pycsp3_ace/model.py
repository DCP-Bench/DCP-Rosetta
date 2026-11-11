# media_selection: a PyCSP3 model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python media_selection.py media_selection.json

from pycsp3 import *


def create_model(instance):
    """Allocate advertising budgets between possible advertising outlets: given a set of
    media options, select the media so that all audiences are reached with minimum campaign
    cost. An audience covered more than once is fine, as long as it is covered at least once."""
    incidence_matrix = instance["incidence_matrix"]  # incidence_matrix[a][m] is 1 when medium m reaches audience a
    media_costs = instance["media_costs"]            # media_costs[m]: the cost of selecting medium m
    n_media = len(media_costs)
    n_audiences = len(incidence_matrix)

    # The media that reach each audience. Audiences reached by the same media give the same
    # constraint, so each distinct set is posted once (PyCSP3 raises 'A group with at least an empty argument list' on identical repeated constraints).
    covering_sets = sorted({tuple(m for m in range(n_media) if incidence_matrix[a][m] == 1) for a in range(n_audiences)})

    # is_selected[m] is 1 when medium m is selected, 0 otherwise.
    is_selected = VarArray(size=n_media, dom={0, 1})

    # total_cost is the campaign cost; the costs are taken as non-negative, so it is at most the sum of all costs.
    total_cost = Var(dom=range(sum(media_costs) + 1))

    satisfy(
        # Every audience is reached by at least one selected medium.
        [Sum(is_selected[m] for m in cover) >= 1 for cover in covering_sets],
        # The campaign cost is the total cost of the selected media.
        total_cost == Sum(media_costs[m] * is_selected[m] for m in range(n_media)),
    )

    # Minimise the campaign cost.
    minimize(total_cost)

    return {"is_selected": is_selected, "min_total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        print("is_selected", "=", values(outputs["is_selected"]))
        print("min_total_cost", "=", value(outputs["min_total_cost"]))
    else:
        print("No solution:", status())

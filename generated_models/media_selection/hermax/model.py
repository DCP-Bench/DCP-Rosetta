# media_selection: a hermax (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install hermax`):
#   python media_selection.py media_selection.json

from hermax.model import Model


def create_model(instance):
    """Media selection: choose which advertising media to buy so that every
    audience is reached by at least one bought medium, at the lowest total cost.
    An audience reached more than once is fine; buying a medium costs its price."""
    # media_costs[j]: the price of buying medium j
    media_costs = instance["media_costs"]
    # incidence_matrix[i][j] = 1 when medium j reaches audience i
    incidence_matrix = instance["incidence_matrix"]
    n_media = len(media_costs)
    n_audiences = len(incidence_matrix)

    m = Model()
    # is_selected[j] is true when medium j is bought
    is_selected = m.bool_vector("is_selected", n_media)

    # Coverage: every audience is reached by at least one bought medium.
    for i in range(n_audiences):
        reaching_media = [is_selected[j] for j in range(n_media) if incidence_matrix[i][j]]
        m &= (sum(reaching_media) >= 1)

    # Objective: the total cost of the bought media, to be minimised.
    total_cost = sum(media_costs[j] * is_selected[j] for j in range(n_media))
    m.obj += total_cost

    return m, {"is_selected": is_selected, "min_total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

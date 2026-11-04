# media_selection: a Z3 (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python media_selection.py media_selection.json

import z3


def create_model(instance):
    """Choose advertising media so that every target audience is reached by at least one
    chosen medium, at the lowest total campaign cost. Reaching an audience more than once
    is fine."""
    incidence = instance["incidence_matrix"]         # incidence[t][m]: 1 if medium m reaches audience t, else 0
    costs = instance["media_costs"]                  # costs[m]: the cost of running medium m
    n_audiences = len(instance["target_audiences"])  # the number of target audiences
    n_media = len(instance["advertising_media"])     # the number of advertising media

    # is_selected[m] is true when medium m is chosen for the campaign
    is_selected = [z3.Bool(f"is_selected_{m}") for m in range(n_media)]

    # picked[m] is 1 when medium m is chosen and 0 otherwise, so that costs can be added up
    picked = [z3.If(is_selected[m], 1, 0) for m in range(n_media)]

    solver = z3.Optimize()

    # Every target audience is reached by at least one chosen medium.
    solver.add([z3.Sum([incidence[t][m] * picked[m] for m in range(n_media)]) >= 1
                for t in range(n_audiences)])

    # The total cost of the chosen media. The campaign spends as little of it as possible.
    total_cost = z3.Sum([costs[m] * picked[m] for m in range(n_media)])

    solver.minimize(total_cost)

    return solver, {"is_selected": is_selected, "min_total_cost": total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

# media_selection: a PuLP (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python media_selection.py media_selection.json

import pulp


def create_model(instance):
    """Choose advertising media so that every target audience is reached by at least one
    chosen medium, at the lowest total campaign cost."""
    target_audiences = instance["target_audiences"]    # the target audiences
    advertising_media = instance["advertising_media"]  # the advertising media
    incidence = instance["incidence_matrix"]           # incidence[t][m] is 1 if medium m reaches audience t
    media_costs = instance["media_costs"]              # media_costs[m] is the cost of medium m
    n_audiences = len(target_audiences)  # the number of target audiences
    n_media = len(advertising_media)     # the number of advertising media

    problem = pulp.LpProblem("media_selection", pulp.LpMinimize)

    # is_selected[m] is 1 when medium m is chosen, and 0 when not
    is_selected = [pulp.LpVariable(f"is_selected_{m}", cat="Binary") for m in range(n_media)]

    # Every audience is reached by at least one chosen medium. Reaching it more than once is fine.
    for t in range(n_audiences):
        problem += pulp.lpSum(incidence[t][m] * is_selected[m] for m in range(n_media)) >= 1

    # The campaign cost is the total cost of the chosen media. Spend as little as possible.
    min_total_cost = pulp.lpSum(media_costs[m] * is_selected[m] for m in range(n_media))
    problem += min_total_cost

    return problem, {"is_selected": is_selected, "min_total_cost": min_total_cost}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

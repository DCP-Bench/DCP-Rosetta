# media_selection: a Choco-solver (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python media_selection.py media_selection.json

from pychoco.model import Model


def create_model(instance):
    """Choose advertising media so that every target audience is reached by at least
    one chosen medium, at the lowest total campaign cost. Reaching an audience more
    than once is fine."""
    target_audiences = instance["target_audiences"]    # the audiences to reach
    advertising_media = instance["advertising_media"]  # the media that can be bought
    incidence = instance["incidence_matrix"]           # incidence[t][m] = 1 if medium m reaches audience t
    media_costs = instance["media_costs"]              # media_costs[m]: the cost of medium m
    n_audiences = len(target_audiences)  # the number of audiences
    n_media = len(advertising_media)     # the number of media

    model = Model()

    # is_selected[m] is true when medium m is bought
    is_selected = [model.boolvar(name=f"is_selected_{m}") for m in range(n_media)]

    # Every audience is reached by at least one chosen medium.
    for t in range(n_audiences):
        model.scalar(is_selected, incidence[t], ">=", 1).post()

    # The total cost of the chosen media, to be minimised.
    min_total_cost = model.intvar(0, sum(media_costs), name="min_total_cost")
    model.scalar(is_selected, media_costs, "=", min_total_cost).post()

    return model, {"is_selected": is_selected, "min_total_cost": min_total_cost}, {"objective": min_total_cost, "maximize": False}


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

# media_selection: a CPLEX (Python) model from DCP Rosetta.
# Download the `media_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/media_selection.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python media_selection.py media_selection.json

from docplex.mp.model import Model


def create_model(instance):
    """Media selection: pick advertising media so that every target audience is reached at the least cost."""
    reaches = instance["incidence_matrix"]  # reaches[t][m] is 1 if medium m reaches audience t
    media_costs = instance["media_costs"]  # media_costs[m]: the cost of using medium m
    audiences = range(len(instance["target_audiences"]))  # the audiences to reach
    media = range(len(instance["advertising_media"]))  # the advertising media to choose from

    model = Model("media_selection")

    # is_selected[m] is 1 when medium m is part of the campaign.
    is_selected = model.binary_var_list(len(media), name="is_selected")

    # Every target audience is reached by at least one selected medium.
    model.add_constraints(model.sum(reaches[t][m] * is_selected[m] for m in media) >= 1 for t in audiences)

    # Minimise the cost of the campaign.
    min_total_cost = model.dot(is_selected, media_costs)
    model.minimize(min_total_cost)

    return model, {"is_selected": is_selected, "min_total_cost": min_total_cost}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.parameters.mip.tolerances.mipgap = 0  # prove the optimum; the default stops within 0.01% of it
    solution = model.solve()

    if solution:  # a proven optimum
        print("Objective value:", round(solution.objective_value))

        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)

# session2_color_simple: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install ortools`):
#   python session2_color_simple.py session2_color_simple.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Give each country a colour, an integer starting from 1, so that two
    neighbouring countries never share a colour, using as few colours as possible."""
    graph = instance["graph"]  # the pairs of neighbouring countries
    n_countries = max(max(pair) for pair in graph)  # the number of countries

    model = cp_model.CpModel()

    # The colour of each country.
    colors = [model.new_int_var(1, n_countries, f"color_{i}") for i in range(n_countries)]

    # Neighbouring countries get different colours.
    for a, b in graph:
        model.add(colors[a - 1] != colors[b - 1])

    # The highest colour in use.
    highest = model.new_int_var(1, n_countries, "highest")
    model.add_max_equality(highest, colors)
    # Minimise the highest colour.
    model.minimize(highest)

    return model, {"colors": colors}


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

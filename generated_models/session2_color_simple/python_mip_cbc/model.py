# session2_color_simple: a Python-MIP (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python session2_color_simple.py session2_color_simple.json

import mip


def create_model(instance):
    """Give each country a colour, an integer starting from 1, so that two
    neighbouring countries never share a colour, using as few colours as possible."""
    graph = instance["graph"]  # each pair [a, b] names two neighbouring countries, numbered from 1
    n_countries = max(max(pair) for pair in graph)  # the countries are numbered 1 to n_countries

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # has_colour[i][c] is 1 when country i+1 has colour c+1, and 0 otherwise
    has_colour = [
        [model.add_var(f"has_colour_{i}_{c}", var_type=mip.BINARY) for c in range(n_countries)]
        for i in range(n_countries)
    ]
    # colors[i] is the colour of country i+1
    colors = [
        model.add_var(f"colors_{i}", lb=1, ub=n_countries, var_type=mip.INTEGER)
        for i in range(n_countries)
    ]
    # the highest colour in use
    top = model.add_var("top_colour", lb=1, ub=n_countries, var_type=mip.INTEGER)

    # Each country has exactly one colour.
    for i in range(n_countries):
        model.add_constr(mip.xsum(has_colour[i]) == 1)

    # The colour of each country is the one it has.
    for i in range(n_countries):
        model.add_constr(colors[i] == mip.xsum((c + 1) * has_colour[i][c] for c in range(n_countries)))

    # Neighbouring countries cannot share a colour.
    for a, b in graph:
        for c in range(n_countries):
            model.add_constr(has_colour[a - 1][c] + has_colour[b - 1][c] <= 1)

    # Every colour used is at most top. With colours numbered from 1, minimising top
    # minimises the number of colours used.
    for i in range(n_countries):
        model.add_constr(colors[i] <= top)

    model.objective = top

    return model, {"colors": colors}


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

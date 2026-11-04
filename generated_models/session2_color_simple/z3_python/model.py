# session2_color_simple: a Z3 (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python session2_color_simple.py session2_color_simple.json

import z3


def create_model(instance):
    """Give each country a colour, an integer starting from 1, so that two
    neighbouring countries never share a colour, using as few colours as possible."""
    graph = instance["graph"]  # each pair [a, b] names two neighbouring countries
    n_countries = max(max(pair) for pair in graph)  # the countries are 1 to n_countries

    # colors[i] is the colour of country i+1
    colors = [z3.Int(f"colors_{i}") for i in range(n_countries)]

    solver = z3.Optimize()

    # Each colour is an integer from 1 to the number of countries.
    solver.add([c >= 1 for c in colors] + [c <= n_countries for c in colors])

    # Neighbouring countries get different colours.
    solver.add([colors[a - 1] != colors[b - 1] for a, b in graph])

    # The highest colour in use is at least the colour of every country.
    highest = z3.Int("highest")
    solver.add([highest >= c for c in colors])

    # Use as few colours as possible: minimise the highest colour.
    solver.minimize(highest)

    return solver, {"colors": colors}


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

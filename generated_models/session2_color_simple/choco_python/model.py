# session2_color_simple: a Choco-solver (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python session2_color_simple.py session2_color_simple.json

from pychoco.model import Model


def create_model(instance):
    """Colour each country so that two neighbouring countries never share a colour, using as few colours as possible. The colours are the integers 1, 2, ..."""
    graph = instance["graph"]                       # pairs of neighbouring countries
    n_countries = max(max(pair) for pair in graph)  # number of countries

    model = Model()

    # colors[i] is the colour of country i+1. A colour from 1 to n_countries is always enough.
    colors = [model.intvar(1, n_countries, name=f"colors_{i}") for i in range(n_countries)]

    # Neighbouring countries get different colours.
    for a, b in graph:
        model.arithm(colors[a - 1], "!=", colors[b - 1]).post()

    # Number of colours used, which is the highest colour given. As few as possible is wanted.
    n_colours = model.intvar(1, n_countries, name="n_colours")
    model.max(n_colours, colors).post()

    return model, {"colors": colors}, {"objective": n_colours, "maximize": False}


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

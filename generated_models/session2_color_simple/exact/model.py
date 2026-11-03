# session2_color_simple: an Exact (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python session2_color_simple.py session2_color_simple.json

from exact import Exact


def colour_flags(solver, country, lo, hi):
    """Flags for one country: flags[v] is 1 when the country has colour v, and 0 otherwise."""
    flags = {v: f"{country}_is_{v}" for v in range(lo, hi + 1)}
    for flag in flags.values():
        solver.addVariable(flag, 0, 1)

    # Each country has exactly one colour.
    solver.addConstraint([(1, f) for f in flags.values()], True, 1, True, 1)

    # The country's colour is the number whose flag is 1.
    solver.addConstraint([(v, flags[v]) for v in flags] + [(-1, country)], True, 0, True, 0)
    return flags


def create_model(instance):
    """Give each country a colour, an integer starting from 1, so that two
    neighbouring countries never share a colour, using as few colours as possible."""
    graph = instance["graph"]  # the pairs of neighbouring countries, numbered from 1

    # The pairs name every country, so the largest number is the country count.
    n_countries = max(max(pair) for pair in graph)

    solver = Exact()

    # Exact identifies its variables by name.
    # colors[i] is the colour of country i+1. Colours run from 1 to n_countries,
    # which is always enough.
    colors = [f"col{i}" for i in range(n_countries)]
    for name in colors:
        solver.addVariable(name, 1, n_countries)

    # The colour flags of each country.
    flags = {name: colour_flags(solver, name, 1, n_countries) for name in colors}

    # Neighbouring countries never share a colour.
    for left, right in graph:
        a, b = colors[left - 1], colors[right - 1]
        for value in range(1, n_countries + 1):
            solver.addConstraint([(1, flags[a][value]), (1, flags[b][value])], False, 0, True, 1)

    # highest is a colour that no country goes above.
    solver.addVariable("highest", 1, n_countries)

    # No country has a colour above highest.
    for name in colors:
        solver.addConstraint([(1, name), (-1, "highest")], False, 0, True, 0)

    # Use as few colours as possible, so minimize the highest colour.
    solver.setObjective([(1, "highest")], minimize=True)

    return solver, {"colors": colors}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

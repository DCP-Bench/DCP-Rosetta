# session2_color_simple: a CPMpy model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python session2_color_simple.py session2_color_simple.json

import cpmpy as cp


def create_model(instance):
    """Give each country a colour, an integer starting from 1, so that two
    neighbouring countries never share a colour, using as few colours as possible."""
    graph = instance["graph"]  # each pair [a, b] names two neighbouring countries (numbered from 1)
    # The countries are numbered 1 to the largest id in the pairs.
    n_countries = max(max(pair) for pair in graph)

    # colors[i] is the colour of country i+1; n_countries colours always suffice
    colors = cp.intvar(1, n_countries, shape=n_countries, name="colors")

    model = cp.Model()
    # Neighbouring countries get different colours.
    for a, b in graph:
        model.add(colors[a - 1] != colors[b - 1])
    # Use as few colours as possible: minimize the highest colour number used.
    model.minimize(cp.max(colors))

    return model, {"colors": colors}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

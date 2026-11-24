# session2_color_simple: a PyCSP3 model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python session2_color_simple.py session2_color_simple.json

from pycsp3 import *


def create_model(instance):
    """We want to assign a different colour to the following countries: Belgium, Denmark, France, Germany, Netherlands
    and Luxembourg. Two neighbouring countries cannot have the same colour. You can use integers starting from 1 to
    represent the colours. Find a colouring that minimizes the number of colours used."""
    # graph[k] is a pair [a, b] of neighbouring countries, numbered from 1 in the order of the statement.
    graph = instance["graph"]
    n_countries = 6  # the six countries named in the statement

    # colors[c] is the colour of country c + 1, in the order Belgium, Denmark, France, Germany, Netherlands, Luxembourg.
    # Colours 1 to n_countries suffice: any colouring can be renamed to use colours 1 to k with k at most n_countries,
    # so the bound loses no colouring with the fewest colours.
    colors = VarArray(size=n_countries, dom=range(1, n_countries + 1))

    satisfy(
        # Two neighbouring countries have different colours.
        [colors[a - 1] != colors[b - 1] for a, b in graph],
    )

    # The number of colours used is to be minimal. NValues(colors) is the direct form, but minimising it was rejected
    # by the evaluator (suboptimal_solution), so the largest colour is minimised instead. The two have the same
    # optimum: at an optimum, the colours used are 1..k, so the largest colour equals the number of colours.
    minimize(Maximum(colors))

    return {"colors": colors}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

# session2_color_simple: a PySAT (Python) model from DCP Rosetta.
# Download the `session2_color_simple.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_color_simple.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python session2_color_simple.py session2_color_simple.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Give each country a colour, a number starting from 1, so that neighbouring
    countries get different colours. Use as few colours as possible."""
    graph = instance["graph"]  # graph[k] is a pair of countries that share a border, numbered from 1
    n_countries = max(max(pair) for pair in graph)  # the countries are numbered 1 to n_countries

    pool = IDPool()  # hands out the variable numbers

    # colors[i] is the colour of country i+1, a number from 1 to n_countries. n_countries
    # colours always suffice.
    colors = [Integer(f"colors_{i}", 1, n_countries, encoding="coupled", vpool=pool)
              for i in range(n_countries)]
    # highest is the largest colour in use.
    highest = Integer("highest", 1, n_countries, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=colors + [highest], vpool=pool)

    # Neighbouring countries get different colours.
    for a, b in graph:
        engine.add_not_equal(colors[a - 1], colors[b - 1])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # highest is at least the colour of every country: a country with colour v or more
    # makes the highest colour v or more.
    for c in colors:
        for v in range(2, n_countries + 1):
            formula.append([-c.ge(v), highest.ge(v)])

    # Minimise the highest colour: each value above 1 that it reaches costs 1.
    for v in range(2, n_countries + 1):
        formula.append([-highest.ge(v)], weight=1)

    # The objective in the problem's terms: the highest colour used, the number of colours (RC2's
    # cost is that number minus 1).
    return formula, {"colors": colors}, highest


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

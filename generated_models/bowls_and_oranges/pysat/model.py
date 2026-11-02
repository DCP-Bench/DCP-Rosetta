# bowls_and_oranges: a PySAT (Python) model from DCP Rosetta.
# Download the `bowls_and_oranges.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bowls_and_oranges.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python bowls_and_oranges.py bowls_and_oranges.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Place all the oranges in bowls that stand in a line one metre apart, at most one
    orange per bowl, so that no three oranges A, B and C have the distance from A to B equal
    to the distance from B to C."""
    n_bowls = instance["n"]    # the number of bowls, numbered 1 to n along the line
    n_oranges = instance["m"]  # the number of oranges

    pool = IDPool()

    # x[i] is the bowl of orange i, with the oranges listed in ascending order of bowl
    x = [Integer(f"x_{i}", 1, n_bowls, vpool=pool) for i in range(n_oranges)]
    engine = IntegerEngine(vars=x, vpool=pool)
    formula = engine.clausify()

    # Each orange lies in a later bowl than the orange before it, so no bowl holds two oranges.
    for i in range(n_oranges - 1):
        for p in range(1, n_bowls + 1):
            for q in range(1, p + 1):
                formula.append([-x[i].equals(p), -x[i + 1].equals(q)])

    # occupied[p] is true when bowl p holds an orange.
    occupied = {p: pool.id(("occupied", p)) for p in range(1, n_bowls + 1)}
    for i in range(n_oranges):
        for p in range(1, n_bowls + 1):
            formula.append([-x[i].equals(p), occupied[p]])

    # Three oranges are never evenly spaced: bowls p, p + d and p + 2d are never all occupied.
    for p in range(1, n_bowls + 1):
        for d in range(1, (n_bowls - p) // 2 + 1):
            formula.append([-occupied[p], -occupied[p + d], -occupied[p + 2 * d]])

    return formula, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

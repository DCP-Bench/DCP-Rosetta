# dinner: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dinner.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python dinner.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Twenty people go to dinner: grandparents, parents and children. The bill is
    $20. How many of each go?"""
    pool = IDPool()  # names the variables of the model

    # the number of grandparents at dinner, from 1 to 6
    grandparents = Integer("grandparents", 1, 6, vpool=pool)
    # the number of parents at dinner, from 1 to 10
    parents = Integer("parents", 1, 10, vpool=pool)
    # the number of children at dinner, from 1 to 40
    children = Integer("children", 1, 40, vpool=pool)

    engine = IntegerEngine(vars=[grandparents, parents, children], vpool=pool)  # the constraints

    # The bill is $20. Prices are doubled so that a child's $0.50 is a whole number: a
    # grandparent costs 6, a parent 4, a child 1, and the bill is 40.
    engine.add_linear(6 * grandparents + 4 * parents + children == 40)
    # There are 20 people in total.
    engine.add_linear(grandparents + parents + children == 20)

    return engine.clausify(), {"grandparents": grandparents, "parents": parents,
                               "children": children}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

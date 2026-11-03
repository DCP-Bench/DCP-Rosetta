# cur_num: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python cur_num.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    pool = IDPool()

    # The peculiar number, from 1 to 9999 so that adding 1 gives at most 10000
    peculiar = Integer("peculiar", 1, 9999, vpool=pool)
    # The square root of the peculiar number plus 1
    root_of_number = Integer("root_of_number", 1, 100, vpool=pool)
    # The square root of half the peculiar number plus 1
    root_of_half = Integer("root_of_half", 1, 100, vpool=pool)
    engine = IntegerEngine(vars=[peculiar, root_of_number, root_of_half], vpool=pool)
    formula = engine.clausify()

    # 48 is the known example, so it is not the answer.
    formula.append([-peculiar.equals(48)])

    for root in range(1, 101):
        # The peculiar number plus 1 is the square of root_of_number.
        value = root * root - 1
        if 1 <= value <= 9999:
            formula.append([-root_of_number.equals(root), peculiar.equals(value)])
        else:
            formula.append([-root_of_number.equals(root)])

        # The peculiar number is twice a number c, and c + 1 is the square of root_of_half.
        value = 2 * (root * root - 1)
        if 1 <= value <= 9999:
            formula.append([-root_of_half.equals(root), peculiar.equals(value)])
        else:
            formula.append([-root_of_half.equals(root)])

    return formula, {"peculiar": peculiar}


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

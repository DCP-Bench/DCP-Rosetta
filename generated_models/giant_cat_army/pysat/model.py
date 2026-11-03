# giant_cat_army: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python giant_cat_army.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Start from 0 and build a list of distinct whole numbers, each at most 60, by
    adding 5, adding 7 or taking the square root of the last number. The list has 24
    numbers, ends with 14, and contains 2 and then 10, in that order, with anything
    between them."""
    max_value = 60  # the largest number allowed in the list
    n_entries = 24  # the number of entries in the list

    pool = IDPool()
    # x[i] is the i-th number of the list.
    x = [Integer(f"x_{i}", 0, max_value, vpool=pool) for i in range(n_entries)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # All numbers in the list are different.
    engine.add_alldifferent(x)
    cnf = engine.clausify()

    # The list starts with 0 and ends with 14.
    cnf.append([x[0].equals(0)])
    cnf.append([x[n_entries - 1].equals(14)])

    # Each number follows from the one before it by adding 5, adding 7, or taking the
    # square root of a square.
    for i in range(n_entries - 1):
        for v in range(max_value + 1):
            # successors: the numbers that may follow v
            successors = [w for w in (v + 5, v + 7) if w <= max_value]
            # root: the square root of v, when v is a square
            root = int(v ** 0.5)
            if root * root == v:
                successors.append(root)
            cnf.append([-x[i].equals(v)] + [x[i + 1].equals(w) for w in successors])

    # 10 appears in the list, and wherever it does, 2 appears earlier.
    cnf.append([x[j].equals(10) for j in range(n_entries)])
    for j in range(1, n_entries):
        cnf.append([-x[j].equals(10)] + [x[i].equals(2) for i in range(1, j)])

    return cnf, {"x": x}


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

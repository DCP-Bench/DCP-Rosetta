# ages_of_the_sons: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/ages_of_the_sons.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python ages_of_the_sons.py

from itertools import product

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """An old man says the product of his three sons' ages is 36. Knowing the sum
    of the ages is still not enough for a mathematician to find them, but once
    told that the oldest son has blue eyes (so there is a unique oldest) he can.
    What are the ages of the three sons?"""
    pool = IDPool()

    # The ages of the sons, oldest first. Each is at most 36, since the three ages multiply to 36.
    ages = [Integer(f"A{k}", 0, 36, vpool=pool) for k in (1, 2, 3)]
    # Another triple of ages, oldest first, that fits the mathematician's clues. Its oldest son differs from the sons' oldest.
    other = [Integer(f"B{k}", 0, 36, vpool=pool) for k in (1, 2, 3)]

    engine = IntegerEngine(vars=ages + other, vpool=pool)

    # The other triple has the same sum as the sons' ages.
    engine.add_linear(ages[0] + ages[1] + ages[2] == other[0] + other[1] + other[2])

    cnf = engine.clausify()

    # The sons' ages multiply to 36, and the oldest son is strictly older than the second.
    # Every triple of ages that is not like this is ruled out.
    for triple in product(range(37), repeat=3):
        if not (triple[0] * triple[1] * triple[2] == 36 and triple[0] > triple[1] >= triple[2]):
            cnf.append([-ages[k].equals(triple[k]) for k in range(3)])

    # The other triple also multiplies to 36, with its ages in order from oldest. Every
    # triple that is not like this is ruled out.
    for triple in product(range(37), repeat=3):
        if not (triple[0] * triple[1] * triple[2] == 36 and triple[0] >= triple[1] >= triple[2]):
            cnf.append([-other[k].equals(triple[k]) for k in range(3)])

    # The other triple's oldest son is a different age from the sons' oldest.
    for value in range(37):
        cnf.append([-ages[0].equals(value), -other[0].equals(value)])

    return cnf, {"A1": ages[0], "A2": ages[1], "A3": ages[2]}


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

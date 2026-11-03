# abbots_puzzle: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/abbots_puzzle.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python abbots_puzzle.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """100 bushels of corn are distributed among 100 people: each man receives
    three bushels, each woman two and each child half a bushel, and there are
    five times as many women as men. Find the number of men, women and children."""
    pool = IDPool()

    # The number of men. Women are at most 100 and there are five times as many women as men, so at most 20 men.
    men = Integer("men", 0, 20, vpool=pool)
    # The number of women.
    women = Integer("women", 0, 100, vpool=pool)
    # The number of children.
    children = Integer("children", 0, 100, vpool=pool)

    engine = IntegerEngine(vars=[men, women, children], vpool=pool)

    # There are 100 people.
    engine.add_linear(men + women + children == 100)
    # The bushels add up to 100. Counted in half bushels, a man gets 6, a woman 4 and a child 1, and 100 bushels is 200 half bushels.
    engine.add_linear(6 * men + 4 * women + children == 200)
    # There are five times as many women as men.
    engine.add_linear(5 * men - women == 0)

    return engine.clausify(), {"men": men, "women": women, "children": children}


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

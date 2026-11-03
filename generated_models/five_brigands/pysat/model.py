# five_brigands: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python five_brigands.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# Each brigand's factor in the second condition, times 6 so that the factors are whole
# numbers: Alfonso 12 becomes 72, Benito 3 becomes 18, Carlos 1 becomes 6, Diego 1/2 becomes 3,
# Esteban 1/3 becomes 2.
TIMES_SIX = {"A": 72, "B": 18, "C": 6, "D": 3, "E": 2}


def create_model(instance):
    """Five Spanish brigands, Alfonso, Benito, Carlos, Diego and Esteban, have
    captured exactly 200 doubloons altogether. If Alfonso had twelve times as
    much, Benito three times as much, Carlos the same amount, Diego half as
    much and Esteban one third as much, they would still have 200 doubloons
    altogether. No brigand has less than one doubloon. How many has each?"""
    pool = IDPool()

    # share[name] is the number of doubloons of that brigand: at least one, and at most
    # what the second condition leaves once the other four have their least.
    total_coefficients = sum(TIMES_SIX.values())
    share = {name: Integer(name, 1, min(200, (1200 - (total_coefficients - c)) // c), vpool=pool)
             for name, c in TIMES_SIX.items()}
    engine = IntegerEngine(vars=list(share.values()), vpool=pool)

    # Together they have 200 doubloons.
    engine.add_linear(sum(share[name] for name in TIMES_SIX) == 200)
    # With the changed amounts they would still have 200 doubloons (times 6).
    engine.add_linear(sum(c * share[name] for name, c in TIMES_SIX.items()) == 1200)

    return engine.clausify(), share


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

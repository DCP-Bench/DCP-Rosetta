# session1_bank_card: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python session1_bank_card.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A four-digit PIN abcd has four different digits, the two-digit number cd is
    3 times the two-digit number ab, and the two-digit number da is 2 times the
    two-digit number bc. Find the PIN."""
    pool = IDPool()

    # The digits a, b, c, d of the PIN, each from 0 to 9
    digits = [Integer(name, 0, 9, vpool=pool) for name in ("a", "b", "c", "d")]
    a, b, c, d = digits
    engine = IntegerEngine(vars=digits, vpool=pool)

    # No two digits of the PIN are the same.
    engine.add_alldifferent(digits)

    # The two-digit number cd is 3 times the two-digit number ab.
    engine.add_linear(10 * c + d == 3 * (10 * a + b))

    # The two-digit number da is 2 times the two-digit number bc.
    engine.add_linear(10 * d + a == 2 * (10 * b + c))

    return engine.clausify(), {"a": a, "b": b, "c": c, "d": d}


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

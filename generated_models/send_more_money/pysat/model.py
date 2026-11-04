# send_more_money: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python send_more_money.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a different digit so that SEND + MORE = MONEY
    holds, with no leading zero in any word."""
    # Every variable of the model comes from this pool.
    pool = IDPool()
    # The digit each letter stands for, from 0 to 9. S starts SEND and M starts MORE and MONEY,
    # so neither is zero.
    letters = {name: Integer(name, 1 if name in "sm" else 0, 9, vpool=pool) for name in "sendmory"}
    # The same digits under their letters, for the sums below.
    s, e, n, d, m, o, r, y = (letters[name] for name in "sendmory")
    # The model: the digits and the constraints on them.
    engine = IntegerEngine(vars=list(letters.values()), vpool=pool)

    # Different letters stand for different digits.
    engine.add_alldifferent(list(letters.values()))

    # The sum of SEND and MORE is MONEY, each word read as a decimal number.
    engine.add_linear(1000 * s + 100 * e + 10 * n + d + 1000 * m + 100 * o + 10 * r + e
                      == 10000 * m + 1000 * o + 100 * n + 10 * e + y)

    return engine.clausify(), letters


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

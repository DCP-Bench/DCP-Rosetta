# session5_hardy_1729_square: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python session5_hardy_1729_square.py

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares of the
    first two equals the sum of the squares of the other two: a^2 + b^2 = c^2 + d^2."""
    low, high = 1, 100  # the numbers lie from low to high, both included

    pool = IDPool()
    # a, b, c and d are the four numbers
    numbers = [Integer(name, low, high, vpool=pool) for name in "abcd"]
    a, b, c, d = numbers
    engine = IntegerEngine(vars=numbers, vpool=pool)

    # The four numbers are all different.
    engine.add_alldifferent(numbers)
    cnf = engine.clausify()

    # sum_is[s] is true when the common sum of squares is s. Each pair of values for a and b,
    # and each pair of values for c and d, makes the sum of its squares true. At most one sum
    # can be true, so both pairs have the same sum of squares.
    sum_is = {}
    for first, second in ((a, b), (c, d)):
        for u in range(low, high + 1):
            for v in range(low, high + 1):
                s = u * u + v * v
                if s not in sum_is:
                    sum_is[s] = pool.id(("sum", s))
                cnf.append([-first.equals(u), -second.equals(v), sum_is[s]])
    cnf.extend(CardEnc.atmost(lits=list(sum_is.values()), bound=1, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    return cnf, {"a": a, "b": b, "c": c, "d": d}


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

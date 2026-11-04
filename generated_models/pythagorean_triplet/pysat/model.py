# pythagorean_triplet: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python pythagorean_triplet.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc, EncType


def create_model(instance):
    """Find natural numbers a, b and c with a^2 + b^2 = c^2 whose sum a + b + c is 1000."""
    total = 1000  # the sum a + b + c
    # a, b and c are at least 1 and at most 500. They add up to 1000, and each is less than the
    # sum of the other two, so each is below 500.
    low, high = 1, 500
    n_bits = high.bit_length()                  # binary digits needed for a number up to high
    n_square_bits = (high * high).bit_length()  # binary digits needed for its square

    pool = IDPool()
    # a, b and c: the three members of the triplet
    numbers = {name: Integer(name, low, high, vpool=pool) for name in "abc"}
    engine = IntegerEngine(vars=list(numbers.values()), vpool=pool)
    # The clauses of the model.
    cnf = engine.clausify()

    # value_bits[name]: the binary digits of the number name. square_bits[name]: the binary
    # digits of its square.
    value_bits, square_bits = {}, {}
    for name, x in numbers.items():
        value_bits[name] = [pool.id((name, "bit", k)) for k in range(n_bits)]
        square_bits[name] = [pool.id((name, "square_bit", k)) for k in range(n_square_bits)]
        # Once a number is fixed, its binary digits and the digits of its square are fixed too.
        for v in range(low, high + 1):
            for k in range(n_bits):
                bit = value_bits[name][k]
                cnf.append([-x.equals(v), bit if (v >> k) & 1 else -bit])
            for k in range(n_square_bits):
                bit = square_bits[name][k]
                cnf.append([-x.equals(v), bit if ((v * v) >> k) & 1 else -bit])

    # a + b + c is 1000. The sum runs over the binary digits of the three numbers, each digit
    # weighted by its value.
    cnf.extend(PBEnc.equals(
        lits=[bit for name in "abc" for bit in value_bits[name]],
        weights=[1 << k for name in "abc" for k in range(n_bits)],
        bound=total, vpool=pool, encoding=EncType.bdd).clauses)

    # a^2 + b^2 = c^2, written as a sum over the binary digits of the squares, with the digits of
    # c^2 subtracted. The squares reach about 2^18, so a plain sum is used rather than a
    # diagram, which would be too large.
    cnf.extend(PBEnc.equals(
        lits=[bit for name in "abc" for bit in square_bits[name]],
        weights=[(1 << k) * (-1 if name == "c" else 1)
                 for name in "abc" for k in range(n_square_bits)],
        bound=0, vpool=pool, encoding=EncType.adder).clauses)

    return cnf, {name: numbers[name] for name in "abc"}


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

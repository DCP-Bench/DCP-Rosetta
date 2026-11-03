# divisible_by_1_through_9: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python divisible_by_1_through_9.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find a 10-digit number that uses each digit 0 to 9 exactly once, where the
    number formed by its first n digits is divisible by n, for n = 1 to 10."""
    # The number has 10 digits; the problem states this, so the instance holds no data.
    n_digits = 10

    pool = IDPool()
    # x[i] = the i-th digit of the number, read from the left. Direct encoding: ten values each.
    x = [Integer(f"x{i}", 0, 9, vpool=pool) for i in range(n_digits)]
    # The engine gets its own copy of the list: it keeps the list it is given and
    # add_var appends to it, which would add the quotients below to the digits output.
    engine = IntegerEngine(vars=list(x), vpool=pool)

    # each of the digits 0..9 is used exactly once
    engine.add_alldifferent(x)

    # the number formed by the first k digits, x[0] x[1] ... x[k-1], is divisible by k.
    # That number is sum(x[j] * 10**(k-1-j)), and only its remainder modulo k matters, so each
    # place value is replaced by its remainder modulo k. This keeps the coefficients below k
    # instead of up to 10**9, and the constraint says sum(c[j] * x[j]) == k * q for some integer
    # q, whose bound is the largest value that reduced sum can take.
    for k in range(1, n_digits + 1):
        coefficients = [pow(10, k - 1 - j, k) for j in range(k)]
        terms = [(c, x[j]) for j, c in enumerate(coefficients) if c != 0]
        if not terms:
            continue  # every place value is a multiple of k (always the case for k = 1)
        reduced = sum(c * digit for c, digit in terms)
        q = Integer(f"q{k}", 0, sum(c * 9 for c, _ in terms) // k, vpool=pool)
        engine.add_var(q)
        engine.add_linear(reduced - k * q == 0)

    # The digits of the number, read from left to right.
    return engine.clausify(), {"digits": x}


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

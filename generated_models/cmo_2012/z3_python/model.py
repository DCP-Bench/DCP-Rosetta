# cmo_2012: a Z3 (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python cmo_2012.py cmo_2012.json

import z3


def is_prime(value):
    """True when value is a prime number, by trial division."""
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime number and
    a * b is a perfect square n^2, find the smallest value of a no less than a
    given minimum."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the largest value any of the numbers may take

    # the primes below max_val, the possible values of p
    primes = [value for value in range(2, max_val) if is_prime(value)]

    # Each number has this many bits, so that a * b and n * n do not wrap around.
    width = 2 * max_val.bit_length() + 1

    def const(value):
        return z3.BitVecVal(value, width)

    a_bv = z3.BitVec("a", width)  # the larger integer
    b_bv = z3.BitVec("b", width)  # the smaller integer, larger than 0
    n_bv = z3.BitVec("n", width)  # the square root of a * b
    p_bv = z3.BitVec("p", width)  # the prime a - b

    solver = z3.Optimize()

    # Each number stays within its range.
    solver.add(z3.UGE(a_bv, const(max(min_a, 0))), z3.ULE(a_bv, const(max_val)),
               z3.UGE(b_bv, const(1)), z3.ULE(b_bv, const(max_val)),
               z3.ULE(n_bv, const(max_val)),
               z3.UGE(p_bv, const(2)), z3.ULE(p_bv, const(max_val)))

    # p is a prime, so a - b is prime.
    solver.add(z3.Or([p_bv == const(q) for q in primes]))

    # a is at least b, and a - b is the prime p.
    solver.add(z3.UGE(a_bv, b_bv), p_bv == a_bv - b_bv)

    # a * b is a perfect square.
    solver.add(a_bv * b_bv == n_bv * n_bv)

    # The answers are read as ordinary whole numbers.
    a, b, n, p = (z3.BV2Int(v) for v in (a_bv, b_bv, n_bv, p_bv))

    # Find the smallest a.
    solver.minimize(a)

    return solver, {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

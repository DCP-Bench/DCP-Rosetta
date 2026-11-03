# cmo_2012: a Python-MIP (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python cmo_2012.py cmo_2012.json

import mip


def is_prime(value):
    """True when value is a prime number."""
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
    given minimum. b must be larger than 0."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the largest value a may take; b, n and p stay below it

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # a: the larger number
    a = model.add_var("a", lb=min_a, ub=max_val, var_type=mip.INTEGER)
    # b: the smaller number
    b = model.add_var("b", lb=1, ub=max_val - 1, var_type=mip.INTEGER)
    # p: the prime a - b
    p = model.add_var("p", lb=2, ub=max_val - 1, var_type=mip.INTEGER)
    # n: the square root of a * b
    n = model.add_var("n", lb=1, ub=max_val - 1, var_type=mip.INTEGER)

    # the number of powers of two needed to reach max_val
    n_bits = max_val.bit_length()
    # b_digit[k] and n_digit[k] are the digits of b and n for the power 2^k, each 0 or 1
    b_digit = [model.add_var(f"b_digit_{k}", var_type=mip.BINARY) for k in range(n_bits)]
    n_digit = [model.add_var(f"n_digit_{k}", var_type=mip.BINARY) for k in range(n_bits)]

    def product_terms(x, digits, prefix):
        # terms[k] is x when digits[k] is 1, and 0 otherwise.
        terms = []
        for k, digit in enumerate(digits):
            term = model.add_var(f"{prefix}_{k}", lb=0, ub=max_val, var_type=mip.INTEGER)
            model.add_constr(term <= x)
            model.add_constr(term <= max_val * digit)
            model.add_constr(term >= x - max_val * (1 - digit))
            terms.append(term)
        return terms

    # b and n are the sums of their powers of two.
    model.add_constr(b == mip.xsum((2**k) * b_digit[k] for k in range(n_bits)))
    model.add_constr(n == mip.xsum((2**k) * n_digit[k] for k in range(n_bits)))

    # ab_terms[k] is a times the digit of b, and nn_terms[k] is n times the digit of n.
    ab_terms = product_terms(a, b_digit, "ab_term")
    nn_terms = product_terms(n, n_digit, "nn_term")

    # a * b is the perfect square n * n.
    model.add_constr(
        mip.xsum((2**k) * ab_terms[k] for k in range(n_bits))
        == mip.xsum((2**k) * nn_terms[k] for k in range(n_bits))
    )

    # The primes below max_val. p is one of them.
    primes = [value for value in range(2, max_val) if is_prime(value)]
    # prime_pick[i] is 1 when p is primes[i], and 0 otherwise.
    prime_pick = [model.add_var(f"prime_pick_{i}", var_type=mip.BINARY) for i in range(len(primes))]
    # Exactly one prime is picked.
    model.add_constr(mip.xsum(prime_pick) == 1)
    # p is the picked prime.
    model.add_constr(p == mip.xsum(q * prime_pick[i] for i, q in enumerate(primes)))

    # a - b is the prime p.
    model.add_constr(a - b == p)

    # The square root of a * b lies strictly between b and a.
    model.add_constr(n >= b + 1)
    model.add_constr(n <= a - 1)

    # The smallest such a.
    model.objective = a

    return model, {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

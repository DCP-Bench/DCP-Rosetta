# cmo_2012: a CPMpy model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python cmo_2012.py cmo_2012.json

import cpmpy as cp


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

    primes = [value for value in range(2, max_val) if is_prime(value)]  # the primes below max_val

    a = cp.intvar(min_a, max_val, name="a")  # the larger integer
    b = cp.intvar(1, max_val, name="b")      # the smaller integer, larger than 0
    n = cp.intvar(0, max_val, name="n")      # the square root of a * b
    p = cp.intvar(2, max_val, name="p")      # the prime a - b

    model = cp.Model()

    # p is one of the primes below max_val.
    model.add(cp.InDomain(p, primes))

    # a - b is the prime p.
    model.add(a >= b)
    model.add(p == a - b)

    # a * b is a perfect square.
    model.add(a * b == n * n)

    # Find the smallest a.
    model.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

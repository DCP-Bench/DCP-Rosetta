# cmo_2012: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install ortools`):
#   python cmo_2012.py cmo_2012.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime number and a * b is
    a perfect square n^2, find the smallest value of a no less than a given minimum.
    Also, b should be larger than 0."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the upper bound on a, b, n and p

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

    # the primes below max_val
    prime_list = [value for value in range(2, max_val) if is_prime(value)]

    model = cp_model.CpModel()

    # a: the larger number
    a = model.new_int_var(min_a, max_val, "a")
    # b: the smaller number
    b = model.new_int_var(1, max_val, "b")
    # n: the square root of a * b
    n = model.new_int_var(0, max_val, "n")
    # p: the prime a - b
    p = model.new_int_var_from_domain(cp_model.Domain.from_values(prime_list), "p")

    # a is at least b, and a - b is the prime p.
    model.add(a >= b)
    model.add(p == a - b)

    # product is a * b, and square is n * n.
    product = model.new_int_var(0, max_val * max_val, "product")
    square = model.new_int_var(0, max_val * max_val, "square")
    model.add_multiplication_equality(product, [a, b])
    model.add_multiplication_equality(square, [n, n])
    # a * b is a perfect square.
    model.add(product == square)

    # Minimize a.
    model.minimize(a)

    return model, {"a": a, "b": b, "n": n, "p": p}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

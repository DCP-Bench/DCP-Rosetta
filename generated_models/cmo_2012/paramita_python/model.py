# cmo_2012: a Paramita (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python cmo_2012.py cmo_2012.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, add_to_weighted_container, to_cnf,
)


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


def binary_number(name, n_digits):
    # digits[i] is the binary digit of weight 2 ** i
    digits = [Bool(f"{name}_bit_{i}") for i in range(n_digits)]
    return digits, sum((2 ** i) * digits[i] for i in range(n_digits))


def unary_count(name, length):
    # ge[t] is true when the count is at least t + 1
    ge = [Bool(f"{name}_ge_{t}") for t in range(1, length + 1)]
    # a count of at least t + 2 is also at least t + 1
    cons = [If(ge[t + 1], ge[t]) for t in range(length - 1)]
    return ge, cons, sum(ge)


def product_bits(name, x_bits, y_bits):
    # the binary digits of x * y, lowest first, and the rules that fix them
    n_digits = len(x_bits)  # binary digits in each factor
    n_product_digits = 2 * n_digits  # binary digits in the product
    cons = []  # the rules of the multiplication
    result = []  # the digits of the product
    carry = None  # the count carried into the next column; none for the lowest column
    for k in range(n_product_digits):
        # t is true when digit i of x and digit j of y are both 1, and i + j = k
        column = []
        for i in range(n_digits):
            j = k - i
            if 0 <= j < n_digits:
                t = Bool(f"{name}_pp_{i}_{j}")
                cons.append(Iff(t, x_bits[i] & y_bits[j]))
                column.append(t)
        r = Bool(f"{name}_bit_{k}")
        result.append(r)
        out_ge, out_cons, out_count = unary_count(f"{name}_carry_{k}", n_digits)
        cons += out_cons
        carry_in = 0 if carry is None else carry
        # the products and the carry in add up to the digit plus twice the carry out
        cons.append(sum(column) + carry_in == r + 2 * out_count)
        carry = out_count
    # nothing is carried past the top column
    cons.append(carry == 0)
    return result, cons


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime number and a * b is
    a perfect square n^2, find the smallest value of a no less than a given minimum."""
    min_a = instance["min_a"]        # the smallest value a may take
    max_val = instance["max_val"]    # the largest value any of a, b, n and p may take
    n_digits = max_val.bit_length()  # binary digits needed to write max_val

    a_bits, a = binary_number("a", n_digits)  # a: the larger integer
    b_bits, b = binary_number("b", n_digits)  # b: the smaller integer
    n_bits, n = binary_number("n", n_digits)  # n: the square root of a * b
    _, p = binary_number("p", n_digits)       # p: the prime a - b

    constraints = []  # the rules the pair of numbers must follow

    # b is at least 1, and a, b and n are no larger than max_val.
    constraints += [b >= 1, a <= max_val, b <= max_val, n <= max_val]

    # a is no less than min_a.
    constraints.append(a >= min_a)

    primes = [q for q in range(2, max_val + 1) if is_prime(q)]  # the primes up to max_val, the possible values of p
    # p_is[q] is true when p is the prime q
    p_is = {q: Bool(f"p_is_{q}") for q in primes}

    # p is one of the primes up to max_val.
    constraints.append(sum(p_is.values()) == 1)
    constraints += [If(p_is[q], p == q) for q in primes]
    constraints.append(p <= max_val)

    # a - b is the prime p.
    constraints.append(a - b == p)

    # a * b is a perfect square: the digits of a * b are those of n * n.
    ab_bits, ab_cons = product_bits("ab", a_bits, b_bits)
    nn_bits, nn_cons = product_bits("nn", n_bits, n_bits)
    constraints += ab_cons + nn_cons
    constraints += [Iff(x, y) for x, y in zip(ab_bits, nn_bits)]

    # a is as small as possible.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-a, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the value of a, minimised (its negation is
    # what the soft clauses maximise).
    return (formula, pool), {"a": a, "b": b, "n": n, "p": p}, a


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")

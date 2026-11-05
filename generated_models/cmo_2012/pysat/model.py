# cmo_2012: a PySAT (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python cmo_2012.py cmo_2012.json

from math import sqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer


def is_prime(value):
    """True when value is a prime number."""
    return value >= 2 and all(value % divisor for divisor in range(2, int(sqrt(value)) + 1))


def create_model(instance):
    """Given two positive integers a and b, where a - b is a prime p and a * b is a perfect
    square n * n, find the smallest a that is at least a given minimum."""
    min_a = instance["min_a"]      # the smallest value a may take
    max_val = instance["max_val"]  # the largest value any of a, b, n and p may take

    pool = IDPool()
    formula = WCNF()

    # a variable fixed to true; the constant false is its negation
    true = pool.id("true")
    formula.append([true])
    false = -true

    # bits per number: enough to write any value up to max_val
    width = max(max_val.bit_length(), 2)

    # the bits of a whole number, lowest first
    def bits(name):
        return [pool.id((name, k)) for k in range(width)]

    # a bit that is 1 exactly when x and y are both 1
    def gate_and(x, y):
        z = pool.id()
        formula.extend([[-z, x], [-z, y], [z, -x, -y]])
        return z

    # the sum bit s and the carry bit of x + y + c
    def full_adder(x, y, c):
        s, carry = pool.id(), pool.id()
        for vx in (True, False):
            for vy in (True, False):
                for vc in (True, False):
                    odd = vx ^ vy ^ vc
                    formula.append([-x if vx else x, -y if vy else y,
                                    -c if vc else c, s if odd else -s])
        formula.extend([[-x, -y, carry], [-x, -c, carry], [-y, -c, carry],
                        [x, y, -carry], [x, c, -carry], [y, c, -carry]])
        return s, carry

    # the sum of two numbers, one bit longer than the longer of them
    def add(xs, ys):
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        out, carry = [], false
        for x, y in zip(xs, ys):
            s, carry = full_adder(x, y, carry)
            out.append(s)
        return out + [carry]

    # the product of two numbers: one shifted sum for each bit of ys
    def multiply(xs, ys):
        total = [false]
        for j, y in enumerate(ys):
            row = [false] * j + [gate_and(x, y) for x in xs]
            total = add(total, row)
        return total

    # the two bit lists spell the same number
    def same(xs, ys):
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        for x, y in zip(xs, ys):
            formula.extend([[-x, y], [x, -y]])

    # xs is at most c: no bit where c is 0 may be 1 while all higher bits match c
    def at_most(xs, c):
        for k in range(len(xs)):
            if not (c >> k) & 1:
                clause = [-xs[k]]
                for j in range(k + 1, len(xs)):
                    clause.append(-xs[j] if (c >> j) & 1 else xs[j])
                formula.append(clause)

    # xs is at least c: no bit where c is 1 may be 0 while all higher bits match c
    def at_least(xs, c):
        for k in range(len(xs)):
            if (c >> k) & 1:
                clause = [xs[k]]
                for j in range(k + 1, len(xs)):
                    clause.append(-xs[j] if (c >> j) & 1 else xs[j])
                formula.append(clause)

    # the whole number over lb..ub that the bits xs spell
    def as_integer(name, xs, lb, ub):
        var = Integer(name, lb, ub, vpool=pool)
        for v in range(lb, ub + 1):
            is_v = var.equals(v)
            spelled = [xs[k] if (v >> k) & 1 else -xs[k] for k in range(width)]
            for s in spelled:
                formula.append([-is_v, s])
            formula.append([is_v] + [-s for s in spelled])
        return var

    # the bits of a, b, n and p
    a, b, n, p = bits("a"), bits("b"), bits("n"), bits("p")

    # Bounds: min_a <= a <= max_val, 1 <= b <= max_val, 0 <= n <= max_val.
    at_least(a, min_a)
    at_most(a, max_val)
    at_least(b, 1)
    at_most(b, max_val)
    at_most(n, max_val)

    # p is a prime below max_val: every other value its bits can spell is forbidden.
    for v in range(1 << width):
        if not (v < max_val and is_prime(v)):
            formula.append([-p[k] if (v >> k) & 1 else p[k] for k in range(width)])

    # a - b is the prime p, so a = b + p.
    same(add(b, p), a)

    # a * b is the perfect square n * n.
    same(multiply(a, b), multiply(n, n))

    # b <= n <= a, since n * n = a * b lies between b * b and a * a.
    # d1 and d2 are the gaps from b up to n and from n up to a.
    same(add(b, bits("d1")), n)
    same(add(n, bits("d2")), a)

    outputs = {
        "a": as_integer("a", a, min_a, max_val),
        "b": as_integer("b", b, 1, max_val),
        "n": as_integer("n", n, 0, max_val),
        "p": as_integer("p", p, 2, max_val),
    }

    # Minimise a: a set bit k of a costs 2^k, so the total cost is the value of a.
    for k in range(width):
        formula.append([-a[k]], weight=1 << k)

    # The objective in the problem's terms: the value of a (as RC2's cost, the weighted bits of a).
    return formula, outputs, outputs["a"]


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

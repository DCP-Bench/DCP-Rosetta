# fibonacci_even: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install "python-sat[pblib]"`) with:
#   python fibonacci_even.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Each new term of the Fibonacci sequence is the sum of the previous two.
    Find the sum of the even-valued terms that do not exceed four million."""
    n = 35                 # the terms f[1] to f[n] are considered
    term_bound = 10 ** 7   # no term exceeds 10**7
    limit = 4_000_000      # the cutoff: a term counts when it is even and below this
    sum_bound = 10 ** 8    # the answer does not exceed 10**8
    term_bits = term_bound.bit_length()  # bits needed for a term
    sum_bits = sum_bound.bit_length()    # bits needed for the answer

    pool = IDPool()
    clauses = []

    # false is a choice fixed to false, used for the bits that are zero
    false = pool.id("false")
    clauses.append([-false])
    # true is a choice fixed to true
    true = -false

    # counter numbers the helper choices, so that each one is new
    counter = [0]

    def fresh():
        """A new choice, free to take either value."""
        counter[0] += 1
        return pool.id(("aux", counter[0]))

    def and_of(lits):
        """A choice that is true exactly when all of lits are true."""
        out = fresh()
        for lit in lits:
            clauses.append([-out, lit])
        clauses.append([out] + [-lit for lit in lits])
        return out

    def or_of(lits):
        """A choice that is true exactly when one of lits is true."""
        out = fresh()
        for lit in lits:
            clauses.append([out, -lit])
        clauses.append([-out] + list(lits))
        return out

    def constant(value, width):
        """The bits of value, least significant first, in width bits."""
        return [true if (value >> k) & 1 else false for k in range(width)]

    def add(a, b, width):
        """The sum of the bit vectors a and b, least significant bit first, in width bits.
        The final carry is forced to 0, so the sum must fit."""
        carry = false
        out = []
        for k in range(width):
            s, c = fresh(), fresh()
            x, y, z = a[k], b[k], carry
            # s is the parity of x, y, z
            clauses.extend([[-x, -y, -z, s], [-x, y, z, s], [x, -y, z, s], [x, y, -z, s],
                            [x, y, z, -s], [x, -y, -z, -s], [-x, y, -z, -s], [-x, -y, z, -s]])
            # c is true when at least two of x, y, z are true
            clauses.extend([[-x, -y, c], [-x, -z, c], [-y, -z, c],
                            [x, y, -c], [x, z, -c], [y, z, -c]])
            out.append(s)
            carry = c
        clauses.append([-carry])
        return out

    def at_most(bits, bound):
        """Forbid the number made by bits from exceeding bound."""
        for k in range(len(bits)):
            if not (bound >> k) & 1:
                clauses.append([-bits[k]] + [-bits[j] for j in range(k + 1, len(bits))
                                             if (bound >> j) & 1])

    def below(bits, bound):
        """A choice that is true exactly when the number made by bits is below bound.
        The bits are compared from the most significant one down."""
        less, equal = false, true
        for k in reversed(range(len(bits))):
            if (bound >> k) & 1:
                less = or_of([less, and_of([equal, -bits[k]])])
                equal = and_of([equal, bits[k]])
            else:
                equal = and_of([equal, -bits[k]])
        return less

    # f[i] is the i-th term as bits, least significant first; f[0] = 0, f[1] = 1, f[2] = 1
    f = [constant(0, term_bits), constant(1, term_bits), constant(1, term_bits)]
    # Each term is the sum of the two before it, and no term exceeds term_bound.
    for i in range(3, n + 1):
        f.append(add(f[i - 1], f[i - 2], term_bits))
        at_most(f[i], term_bound)

    # x[i] is true when term i is counted: it is even and below the limit. Term 0 is never counted.
    x = [false] + [and_of([-f[i][0], below(f[i], limit)]) for i in range(1, n + 1)]

    # total is the answer so far: the counted terms added up one at a time.
    total = constant(0, sum_bits)
    for i in range(1, n + 1):
        # selected: the bits of term i if it is counted, and 0 otherwise
        selected = [and_of([x[i], bit]) for bit in f[i]] + [false] * (sum_bits - term_bits)
        total = add(total, selected, sum_bits)

    # res_bits[k] is bit k of the answer, a 0/1 whole number, so the answer is their weighted sum.
    res_bits = [Integer(f"res{k}", 0, 1, vpool=pool) for k in range(sum_bits)]
    # engine holds the rules for the 0/1 numbers
    engine = IntegerEngine(vars=res_bits, vpool=pool)
    # The answer has the bits of the total.
    for bit, lit in zip(res_bits, total):
        one = bit.equals(1)
        clauses.extend([[-one, lit], [one, -lit]])
    # The answer does not exceed sum_bound.
    at_most([bit.equals(1) for bit in res_bits], sum_bound)
    res = sum(2 ** k * bit for k, bit in enumerate(res_bits))

    # cnf: all the rules together
    cnf = engine.clausify()
    cnf.extend(clauses)
    return cnf, {"res": res}


if __name__ == "__main__":
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # res is a weighted sum of 0/1 Integers: add up each coefficient times its decoded bit
        res = outputs["res"]
        print("res =", res.const + sum(c * var.decode(model) for var, c in res.terms.items()))
    else:
        print("No solution")

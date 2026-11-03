# csplib_041_n_fractions: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python csplib_041_n_fractions.py

from math import gcd

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    pool = IDPool()

    # The nine digits A to I, each from 1 to 9.
    digits = [Integer(name, 1, 9, vpool=pool) for name in "ABCDEFGHI"]
    A, B, C, D, E, F, G, H, I = digits

    # The two-digit numbers BC, EF and HI, each from 11 to 99.
    BC, EF, HI = (Integer(name, 11, 99, vpool=pool) for name in ("BC", "EF", "HI"))
    engine = IntegerEngine(vars=digits + [BC, EF, HI], vpool=pool)

    # The fraction num / den in lowest terms, so that equal fractions compare equal.
    def reduced(num, den):
        g = gcd(num, den)
        return (num // g, den // g)

    # The nine digits are all different.
    engine.add_alldifferent(digits)

    # BC, EF and HI are the numbers with tens digits B, E, H and units digits C, F, I.
    engine.add_linear(BC == 10 * B + C)
    engine.add_linear(EF == 10 * E + F)
    engine.add_linear(HI == 10 * H + I)

    cnf = engine.clausify()

    # The equation has divisions and products of variables, so each fraction is written as a
    # table: is_fraction[k][(num, den)] is true whenever the k-th fraction equals num / den.
    fractions = [(A, BC), (D, EF), (G, HI)]
    is_fraction = []
    for numerator, denominator in fractions:
        table = {}
        for num in range(1, 10):
            for den in range(11, 100):
                value = pool.id(("fraction", numerator.name, num, den))
                cnf.append([-numerator.equals(num), -denominator.equals(den), value])
                table[(num, den)] = value
        is_fraction.append(table)

    # remainder_is[r] is true when 1 minus the third fraction equals r, in lowest terms.
    # The third fraction fixes one remainder, so at most one of them is true.
    remainder_is = {}
    for (num, den), value in is_fraction[2].items():
        remainder = reduced(den - num, den)
        if remainder not in remainder_is:
            remainder_is[remainder] = pool.id(("remainder", remainder))
        cnf.append([-value, remainder_is[remainder]])
    cnf.extend(CardEnc.atmost(lits=list(remainder_is.values()), bound=1, vpool=pool,
                              encoding=EncType.seqcounter).clauses)

    # The first two fractions add up to the remainder of the third. A pair whose sum is no
    # remainder of the third fraction is ruled out.
    for (num1, den1), first in is_fraction[0].items():
        for (num2, den2), second in is_fraction[1].items():
            total = reduced(num1 * den2 + num2 * den1, den1 * den2)
            if total in remainder_is:
                cnf.append([-first, -second, remainder_is[total]])
            else:
                cnf.append([-first, -second])

    return cnf, {name: digit for name, digit in zip("ABCDEFGHI", digits)}


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

"""N fractions: distinct non-zero digits A..I with A / BC + D / EF + G / HI = 1."""
from itertools import product

import hexaly.optimizer as hx

# Every way to write a fraction's three digits (numerator, then the two digits of the denominator) with three
# different non-zero digits
TRIPLES = [t for t in product(range(1, 10), repeat=3) if len(set(t)) == 3]


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each of the three fractions is one entry of the list of digit triples: nine free digits tied by a cubic
    # equation are very hard for Hexaly to search, while a choice among 504 valid triples is not.
    first = [model.array([t[k] for t in TRIPLES]) for k in range(3)]  # the digits of each triple, by position
    choice = [model.int(0, len(TRIPLES) - 1) for _ in range(3)]  # the triple of A/BC, D/EF and G/HI
    A, B, C, D, E, F, G, H, I = (model.at(first[k], choice[f]) for f in range(3) for k in range(3))

    # The nine digits are all different: those within a triple already are, so only digits of
    # different triples are compared
    digits = [[A, B, C], [D, E, F], [G, H, I]]
    for f in range(3):
        for g in range(f + 1, 3):
            for x in digits[f]:
                for y in digits[g]:
                    model.constraint(x != y)

    # BC, EF and HI are the two-digit numbers they spell
    bc, ef, hi = 10 * B + C, 10 * E + F, 10 * H + I
    # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI to stay in integers
    model.constraint(A * ef * hi + D * bc * hi + G * bc * ef == bc * ef * hi)

    return optimizer, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}

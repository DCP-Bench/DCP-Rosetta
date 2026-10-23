from hermax.model import Model


# The problem has no instance parameters, so the digit range 1..9 and the
# place values 10 and 100 are fixed constants of the problem.


def build(instance):
    m = Model()

    # Nine distinct non-zero digits: A B C D E F G H I as indices 0..8.
    d = m.int_vector("d", 9, 1, 9)
    m &= d.all_different()
    A, B, C, D, E, F, G, H, I = [d[k] for k in range(9)]

    counter = [0]
    pending = []

    def fresh(prefix):
        counter[0] += 1
        return f"{prefix}_{counter[0]}"

    pair_cache = {}
    triple_cache = {}

    def pair(i, j):
        # p == d[i] * d[j], as a table over the multiplication of two digits.
        key = tuple(sorted((i, j)))
        if key not in pair_cache:
            p = m.int(fresh("p"), 1, 81)
            rows = [(a, b, a * b) for a in range(1, 10) for b in range(1, 10)]
            pending.append(m.table([d[key[0]], d[key[1]], p], allowed=rows))
            pair_cache[key] = p
        return pair_cache[key]

    def triple(i, j, k):
        # t == d[i] * d[j] * d[k], as a table over three digits.
        key = tuple(sorted((i, j, k)))
        if key not in triple_cache:
            t = m.int(fresh("t"), 1, 729)
            rows = [(a, b, c, a * b * c)
                    for a in range(1, 10) for b in range(1, 10) for c in range(1, 10)]
            pending.append(m.table([d[key[0]], d[key[1]], d[key[2]], t], allowed=rows))
            triple_cache[key] = t
        return triple_cache[key]

    # Clear the denominators of  A/BC + D/EF + G/HI = 1  by multiplying by
    # BC * EF * HI, where BC = 10B + C, EF = 10E + F, HI = 10H + I.
    #
    #   A*EF*HI + D*BC*HI + G*BC*EF == BC*EF*HI
    #
    # Expanding each two-digit factor gives sums of digit triples.

    # A * EF * HI = A * (100 EH + 10 EI + 10 FH + FI)
    lhs_a = [(100, (0, 4, 7)), (10, (0, 4, 8)), (10, (0, 5, 7)), (1, (0, 5, 8))]
    # D * BC * HI = D * (100 BH + 10 BI + 10 CH + CI)
    lhs_d = [(100, (3, 1, 7)), (10, (3, 1, 8)), (10, (3, 2, 7)), (1, (3, 2, 8))]
    # G * BC * EF = G * (100 BE + 10 BF + 10 CE + CF)
    lhs_g = [(100, (6, 1, 4)), (10, (6, 1, 5)), (10, (6, 2, 4)), (1, (6, 2, 5))]
    # BC * EF * HI = (10B + C) * (100 EH + 10 EI + 10 FH + FI)
    rhs = [
        (1000, (1, 4, 7)), (100, (1, 4, 8)), (100, (1, 5, 7)), (10, (1, 5, 8)),
        (100, (2, 4, 7)), (10, (2, 4, 8)), (10, (2, 5, 7)), (1, (2, 5, 8)),
    ]

    lhs = sum(c * triple(*t) for c, t in lhs_a + lhs_d + lhs_g)
    rhs_expr = sum(c * triple(*t) for c, t in rhs)
    m &= (lhs == rhs_expr)
    for c in pending:
        m &= c

    outputs = {
        "A": A, "B": B, "C": C, "D": D, "E": E,
        "F": F, "G": G, "H": H, "I": I,
    }
    return m, outputs

from hermax.model import Model


def build(instance):
    m = Model()

    # Nine digits, each in 1..9, all different: "distinct non-zero digits".
    digits = m.int_vector("digit", 9, 1, 9)
    m &= digits.all_different()
    dig = {name: digits[i] for i, name in enumerate("ABCDEFGHI")}

    # BC, EF, HI are the two-digit numbers 10*tens + units. They are kept as
    # polynomials in the digits, so every product is a product of digits.
    def number(tens, units):
        return {(tens,): 10, (units,): 1}

    def pmul(p, q):
        out = {}
        for k1, c1 in p.items():
            for k2, c2 in q.items():
                key = tuple(sorted(k1 + k2))
                out[key] = out.get(key, 0) + c1 * c2
        return out

    def padd(p, q):
        out = dict(p)
        for k, c in q.items():
            out[k] = out.get(k, 0) + c
        return out

    N1 = number("B", "C")
    N2 = number("E", "F")
    N3 = number("H", "I")
    A = {("A",): 1}
    D = {("D",): 1}
    G = {("G",): 1}

    # Cleared fractions: A/BC + D/EF + G/HI = 1, multiplied by BC*EF*HI,
    # gives A*EF*HI + D*BC*HI + G*BC*EF = BC*EF*HI.
    lhs = padd(padd(pmul(A, pmul(N2, N3)), pmul(D, pmul(N1, N3))),
               pmul(G, pmul(N1, N2)))
    rhs = pmul(N1, pmul(N2, N3))

    # One product variable per monomial, built by looping over the digit
    # factor, so every domain stays within 9 * 81 = 729.
    cache = {}

    def monomial(key):
        nonlocal m
        if len(key) == 1:
            return dig[key[0]]
        if key in cache:
            return cache[key]
        prefix = monomial(key[:-1])
        last = dig[key[-1]]
        hi = prefix.ub * last.ub
        p = m.int("m_" + "".join(key), 0, hi)
        for v in range(prefix.lb, prefix.ub + 1):
            for k in range(last.lb, last.ub + 1):
                m &= (~(prefix == v)) | (~(last == k)) | (p == v * k)
        cache[key] = p
        return p

    # Each monomial goes to binary digits, and the equation is one weighted
    # sum over the bits, which keeps the pseudo-Boolean part small.
    def bits_of(key):
        nonlocal m
        v = monomial(key)
        nbits = max(1, v.ub.bit_length())
        bits = m.bool_vector("b_" + "".join(key), nbits)
        for x in range(v.lb, v.ub + 1):
            for j in range(nbits):
                lit = bits[j] if (x >> j) & 1 else ~bits[j]
                m &= (~(v == x)) | lit
        return bits, nbits

    left = 0
    for k, c in lhs.items():
        bits, nbits = bits_of(k)
        left = left + sum(c * 2 ** j * bits[j] for j in range(nbits))
    right = 0
    for k, c in rhs.items():
        bits, nbits = bits_of(k)
        right = right + sum(c * 2 ** j * bits[j] for j in range(nbits))
    m &= (left == right)

    outputs = {name: dig[name] for name in "ABCDEFGHI"}
    return m, outputs

from hermax.model import Model

# Fixed constants of the problem: 10 digits, prefix lengths 1..10.
# Prefix P_n is divisible by n iff it is divisible by every prime power
# q in MODULI that divides n. Each such residue P_n mod q follows from the
# previous one by P_k mod q = (10 * (P_{k-1} mod q) + d_{k-1}) mod q, so a
# chain of small residues tracks it without ever building the full prefix.
DIGITS = 10
MODULI = [2, 3, 4, 5, 7, 8, 9]


def build(instance):
    m = Model()
    d = m.int_vector("digit", DIGITS, 0, 9)
    m &= d.all_different()
    # A ten-digit number has a non-zero leading digit.
    m &= (d[0] >= 1)

    # residue[q][k] = P_k mod q, for k = 1..DIGITS.
    residue = {}
    for q in MODULI:
        prev = 0  # P_0 mod q = 0
        chain = [None]
        for k in range(1, DIGITS + 1):
            c = m.int(f"res_{q}_{k}", 0, q - 1)
            # 10 * prev + d_{k-1} lies in [0, 10q - 1], so the quotient is in [0, 9].
            carry = m.int(f"carry_{q}_{k}", 0, 9)
            m &= (10 * prev + d[k - 1] == q * carry + c)
            chain.append(c)
            prev = c
        residue[q] = chain

    # Prefix of length n must be divisible by every modulus q that divides n.
    for n in range(1, DIGITS + 1):
        for q in MODULI:
            if n % q == 0:
                m &= (residue[q][n] == 0)

    number = sum(10 ** (DIGITS - 1 - i) * d[i] for i in range(DIGITS))
    return m, {"number": number}

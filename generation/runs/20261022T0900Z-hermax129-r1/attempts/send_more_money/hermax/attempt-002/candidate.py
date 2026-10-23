from hermax.model import Model


def build(instance):
    """
    Send More Money cryptarithmetic puzzle.
    Find unique digits for s, e, n, d, m, o, r, y such that:
    SEND + MORE = MONEY
    Each letter is a unique digit 0-9, first letters (s, m) != 0.
    """

    m = Model()

    # Variables: each letter is a digit 0-9
    letters_vec = m.int_vector("letters", 8, 0, 9)
    s, e, n, d, m_letter, o, r, y = letters_vec

    # All letters are different
    m &= letters_vec.all_different()

    # First letters cannot be zero
    m &= (s >= 1)  # SEND starts with S
    m &= (m_letter >= 1)  # MORE and MONEY start with M

    # Cryptarithmetic constraint: SEND + MORE = MONEY
    # SEND = 1000*s + 100*e + 10*n + d
    # MORE = 1000*m + 100*o + 10*r + e
    # MONEY = 10000*m + 1000*o + 100*n + 10*e + y
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m_letter + 100 * o + 10 * r + e
    money = 10000 * m_letter + 1000 * o + 100 * n + 10 * e + y

    m &= (send + more == money)

    return m, {
        "s": s,
        "e": e,
        "n": n,
        "d": d,
        "m": m_letter,
        "o": o,
        "r": r,
        "y": y,
    }

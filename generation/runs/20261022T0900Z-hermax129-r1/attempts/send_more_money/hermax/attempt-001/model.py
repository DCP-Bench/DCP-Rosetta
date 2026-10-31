"""Send More Money - cryptarithmetic puzzle.

Assign unique digits 0-9 to letters S, E, N, D, M, O, R, Y such that:
  SEND + MORE = MONEY
Leading digits S and M cannot be 0.
"""

from hermax.model import Model


def build(instance):
    m = Model()

    # Each letter is a digit from 0 to 9
    s = m.int("s", 0, 9)
    e = m.int("e", 0, 9)
    n = m.int("n", 0, 9)
    d = m.int("d", 0, 9)
    m_var = m.int("m", 0, 9)
    o = m.int("o", 0, 9)
    r = m.int("r", 0, 9)
    y = m.int("y", 0, 9)

    # All digits must be unique
    letters_vec = m.int_vector("letters", 8, 0, 9)
    m &= letters_vec.all_different()
    m &= (letters_vec[0] == s)
    m &= (letters_vec[1] == e)
    m &= (letters_vec[2] == n)
    m &= (letters_vec[3] == d)
    m &= (letters_vec[4] == m_var)
    m &= (letters_vec[5] == o)
    m &= (letters_vec[6] == r)
    m &= (letters_vec[7] == y)

    # Leading digits cannot be 0
    m &= (s != 0)
    m &= (m_var != 0)

    # Constraint: SEND + MORE = MONEY
    send = 1000 * s + 100 * e + 10 * n + d
    more = 1000 * m_var + 100 * o + 10 * r + e
    money = 10000 * m_var + 1000 * o + 100 * n + 10 * e + y

    m &= (send + more == money)

    outputs = {
        "d": d,
        "e": e,
        "m": m_var,
        "n": n,
        "o": o,
        "r": r,
        "s": s,
        "y": y,
    }

    return m, outputs

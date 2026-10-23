from hermax.model import Model


def build(instance):
    init = instance["isbn_init"]
    n = len(init)

    m = Model()
    # Each digit is 0..9. A given digit fixes its position, -1 leaves it open.
    digits = m.int_vector("isbn", n, 0, 9)
    for i, v in enumerate(init):
        if v != -1:
            m &= (digits[i] == v)

    # An ISBN-13 starts with 978 or 979.
    m &= (digits[0] == 9)
    m &= (digits[1] == 7)
    m &= ((digits[2] == 8) | (digits[2] == 9))

    # Weights 1 and 3 alternate from the first digit. The check digit makes
    # the weighted sum of all 13 digits a multiple of 10.
    total = sum((1 if i % 2 == 0 else 3) * digits[i] for i in range(n))
    q = m.int("q", 0, 9 * 25 // 10)
    m &= (total == 10 * q)

    return m, {"isbn": digits}

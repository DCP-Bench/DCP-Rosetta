from hermax.model import Model


def build(instance):
    m = Model()

    isbn_init = instance["isbn_init"]

    # ISBN-13 is a list of 13 digits, each 0-9
    isbn = m.int_vector("isbn", 13, 0, 9)

    # Constraint: preserve known digits from input
    for i in range(13):
        if isbn_init[i] != -1:
            m &= (isbn[i] == isbn_init[i])

    # Constraint: first 3 digits must be 978 or 979
    m &= ((isbn[0] == 9) & (isbn[1] == 7))  # First two are always 97
    m &= ((isbn[2] == 8) | (isbn[2] == 9))   # Third digit is 8 or 9

    # Constraint: check digit calculation
    # sum = isbn[0]*1 + isbn[1]*3 + isbn[2]*1 + ... + isbn[11]*3
    weights = [1, 3, 1, 3, 1, 3, 1, 3, 1, 3, 1, 3]
    weighted_sum = sum(isbn[i] * weights[i] for i in range(12))

    # Auxiliary variable for the sum modulo 10
    remainder = m.int("remainder", 0, 9)

    # Create a constraint: weighted_sum = 10*q + remainder for some q
    # This means: weighted_sum % 10 = remainder
    # We can encode this as: remainder = weighted_sum - 10 * floor(weighted_sum / 10)

    # Since weighted_sum is bounded, we can use: 0 <= weighted_sum - 10*q < 10
    # where remainder = weighted_sum - 10*q
    # So: q = floor(weighted_sum / 10)
    q = m.int("quotient", 0, 100)  # Upper bound for quotient
    m &= (weighted_sum == 10 * q + remainder)

    # Check digit constraint: isbn[12] = (10 - remainder) % 10
    # This means:
    # - if remainder == 0, then isbn[12] == 0
    # - if remainder == 1, then isbn[12] == 9
    # - if remainder == 2, then isbn[12] == 8
    # ...
    # - if remainder == 9, then isbn[12] == 1

    # Encode as: isbn[12] + remainder == 10 (when remainder > 0)
    #            isbn[12] == 0 (when remainder == 0)
    # Or equivalently: isbn[12] + remainder == 10 or (isbn[12] == 0 and remainder == 0)

    # Use auxiliary booleans for each remainder value
    for r in range(10):
        is_remainder_r = m.bool(f"remainder_is_{r}")
        m &= (is_remainder_r == (remainder == r))

        if r == 0:
            # When remainder is 0, check digit must be 0
            m &= (is_remainder_r <= (isbn[12] == 0))
        else:
            # When remainder is r > 0, check digit is 10 - r
            m &= (is_remainder_r <= (isbn[12] == (10 - r)))

    return m, {"isbn": isbn}

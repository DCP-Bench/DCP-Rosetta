"""ISBN-13: fill the unknown digits (-1) so the number starts with 978 or 979 and has a valid check digit."""
import hexaly.optimizer as hx


def build(instance):
    # isbn_init[i] = the i-th of the 13 digits (0-9), or -1 if that digit is unknown
    known = instance["isbn_init"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # isbn[i] = the i-th digit (0-9) of the complete ISBN-13; isbn[12] is the check digit
    isbn = [model.int(0, 9) for _ in range(13)]
    # The known digits stay
    for i, d in enumerate(known):
        if d != -1:
            model.constraint(isbn[i] == d)
    # An ISBN-13 starts with 978 or 979
    model.constraint(isbn[0] == 9)
    model.constraint(isbn[1] == 7)
    model.constraint(model.or_(isbn[2] == 8, isbn[2] == 9))

    # The check digit is (10 - (sum % 10)) % 10, where the sum is over the first 12 digits
    # multiplied alternately by 1 and 3, starting with 1
    total = model.sum((1 if i % 2 == 0 else 3) * isbn[i] for i in range(12))
    model.constraint(isbn[12] == (10 - total % 10) % 10)

    return optimizer, {"isbn": isbn}

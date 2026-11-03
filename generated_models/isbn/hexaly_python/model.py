"""ISBN-13: fill the unknown digits (-1) so the number starts with 978 or 979 and has a valid check digit."""
import hexaly.optimizer as hx


def build(instance):
    known = instance["isbn_init"]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    isbn = [model.int(0, 9) for _ in range(13)]
    # The known digits stay
    for i, d in enumerate(known):
        if d != -1:
            model.constraint(isbn[i] == d)
    # An ISBN-13 starts with 978 or 979
    model.constraint(isbn[0] == 9)
    model.constraint(isbn[1] == 7)
    model.constraint(model.or_(isbn[2] == 8, isbn[2] == 9))

    # The check digit: weights 1, 3, 1, 3, ... on the first 12 digits, then (10 - sum % 10) % 10
    total = model.sum((1 if i % 2 == 0 else 3) * isbn[i] for i in range(12))
    model.constraint(isbn[12] == (10 - total % 10) % 10)

    return optimizer, {"isbn": isbn}

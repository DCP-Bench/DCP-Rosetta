from hermax.model import Model


def build(instance):
    # This problem has no instance fields. The number 48 is the example from the
    # description and is excluded, so the answer is another number.
    model = Model()

    # The peculiar number lies between 1 and 10000.
    p = model.int("peculiar", 1, 10000)
    model &= (p != 48)

    # Adding 1 gives a square: p + 1 = a * a. Since 101 * 101 > 10001, a lies in 1 .. 101.
    # A constant list of squares indexed by a gives the square as a lookup.
    squares_a = [k * k for k in range(1, 102)]
    a = model.int("a", 1, 101)
    sq_a = model.int("sq_a", 1, 101 * 101)
    model &= ((squares_a @ a) == sq_a)
    model &= (sq_a == p + 1)

    # Half of it, plus 1, is a square: p = 2h and h + 1 = b * b.
    # Since 71 * 71 > 5001, b lies in 1 .. 71.
    h = model.int("half", 0, 5000)
    model &= (p == 2 * h)
    squares_b = [k * k for k in range(1, 72)]
    b = model.int("b", 1, 71)
    sq_b = model.int("sq_b", 1, 71 * 71)
    model &= ((squares_b @ b) == sq_b)
    model &= (sq_b == h + 1)

    return model, {"peculiar": p}

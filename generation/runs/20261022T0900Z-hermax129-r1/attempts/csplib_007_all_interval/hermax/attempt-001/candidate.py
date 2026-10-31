from hermax.model import Model


def build(instance):
    # All-interval series problem
    n = instance["n"]

    m = Model()

    # x is a permutation of {0, 1, ..., n-1}
    x = m.int_vector("x", n, 0, n - 1)
    m &= x.all_different()

    # diffs is a permutation of {1, ..., n-1} representing |x[i+1] - x[i]|
    diffs = m.int_vector("diffs", n - 1, 1, n - 1)
    m &= diffs.all_different()

    # Constraint: diffs[i] == |x[i+1] - x[i]|
    # Use Boolean variables to track the sign
    for i in range(n - 1):
        # positive = (x[i+1] >= x[i])
        positive = m.bool(f"pos_{i}")

        # If positive, then x[i+1] - x[i] == diffs[i]
        m &= ~positive | (x[i + 1] - x[i] == diffs[i])
        # If not positive, then x[i] - x[i+1] == diffs[i]
        m &= positive | (x[i] - x[i + 1] == diffs[i])

    return m, {"x": x, "diffs": diffs}

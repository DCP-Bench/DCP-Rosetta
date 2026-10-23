from hermax.model import Model


def build(instance):
    # Four numbers between 1 and 100 (the range is fixed by the problem).
    lo, hi = 1, 100

    m = Model()
    x = m.int_vector("x", 4, lo, hi)
    a, b, c, d = x[0], x[1], x[2], x[3]

    # The four numbers are different.
    m &= x.all_different()

    # The square of each number as a weighted sum over its value literals:
    # if the number is k, its square is k * k. This avoids an integer
    # variable with 10000 values, which runs out of memory.
    squares = [sum(k * k * (x[i] == k) for k in range(lo, hi + 1)) for i in range(4)]

    # a^2 + b^2 = c^2 + d^2.
    m &= (squares[0] + squares[1] == squares[2] + squares[3])

    return m, {"a": a, "b": b, "c": c, "d": d}

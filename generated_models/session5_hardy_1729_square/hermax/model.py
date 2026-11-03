# session5_hardy_1729_square: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install hermax`) with:
#   python session5_hardy_1729_square.py

from hermax.model import Model


def create_model(instance):
    """Hardy's 1729 squares: find four different numbers a, b, c, d between 1 and 100
    with a^2 + b^2 = c^2 + d^2, and report them as (a, b, c, d)."""
    # The statement fixes the range 1..100 and the instance carries no data, so the
    # instance argument is not read.
    low, high = 1, 100   # the four numbers each lie between 1 and 100

    m = Model()

    # a, b, c, d: the four numbers of the statement
    a, b, c, d = (m.int(name, low, high) for name in ("a", "b", "c", "d"))

    # The four numbers are different.
    m &= m.vector([a, b, c, d]).all_different()

    # sq_x is the square of x. Squaring is not arithmetic hermax can post directly, so
    # each pair (x, x * x) is listed as an allowed row of a table.
    squares = {}
    for name, number in (("a", a), ("b", b), ("c", c), ("d", d)):
        # sq_x: the square of x, between 1 and 10000
        sq = m.int(f"square_{name}", low * low, high * high)
        m &= m.table([number, sq], allowed=[(v, v * v) for v in range(low, high + 1)])
        squares[name] = sq

    # a^2 + b^2 = c^2 + d^2: the sum of the squares of the first two numbers equals
    # the sum of the squares of the other two.
    m &= (squares["a"] + squares["b"] == squares["c"] + squares["d"])

    return m, {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

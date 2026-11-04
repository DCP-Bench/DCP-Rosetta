# session5_hardy_1729_square: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install cpmpy`) with:
#   python session5_hardy_1729_square.py

import cpmpy as cp


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    # The problem fixes its own data, so the instance is not read.
    range_min, range_max = 1, 100

    # x holds the four numbers (a, b, c, d)
    x = cp.intvar(range_min, range_max, shape=4, name="x")
    a, b, c, d = x

    model = cp.Model()
    # The sum of the squares of a and b equals the sum of the squares of c and d.
    model.add(cp.sum(x[:2] ** 2) == cp.sum(x[2:] ** 2))
    # The four numbers are different.
    model.add(cp.AllDifferent(x))

    return model, {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

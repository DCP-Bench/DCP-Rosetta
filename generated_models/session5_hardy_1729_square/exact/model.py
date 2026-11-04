# session5_hardy_1729_square: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install exact numpy`) with:
#   python session5_hardy_1729_square.py

from exact import Exact


def create_model(instance):
    """Find four different numbers a, b, c and d between 1 and 100 such that a^2 + b^2 = c^2 + d^2."""
    # The numbers are whole numbers from 1 to 100.
    lowest, highest = 1, 100
    numbers = ["a", "b", "c", "d"]
    values = range(lowest, highest + 1)

    solver = Exact()

    # Exact identifies its variables by name.
    # Each of the four numbers lies between 1 and 100.
    for name in numbers:
        solver.addVariable(name, lowest, highest)

    # is_value[name][v] is 1 when the number name equals v, and 0 when not.
    is_value = {name: {v: f"{name}_is_{v}" for v in values} for name in numbers}
    for name in numbers:
        for v in values:
            solver.addVariable(is_value[name][v], 0, 1)

    # Each number equals exactly one value.
    for name in numbers:
        solver.addConstraint([(1, is_value[name][v]) for v in values], True, 1, True, 1)

    # Each number is the value it equals.
    for name in numbers:
        solver.addConstraint([(v, is_value[name][v]) for v in values] + [(-1, name)],
                             True, 0, True, 0)

    # No two of the four numbers are equal: each value is taken by at most one of them.
    for v in values:
        solver.addConstraint([(1, is_value[name][v]) for name in numbers], False, 0, True, 1)

    # The squares of a and b add up to the squares of c and d.
    squares = [(v * v, is_value["a"][v]) for v in values] + \
              [(v * v, is_value["b"][v]) for v in values] + \
              [(-v * v, is_value["c"][v]) for v in values] + \
              [(-v * v, is_value["d"][v]) for v in values]
    solver.addConstraint(squares, True, 0, True, 0)

    return solver, {name: name for name in numbers}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

# divisible_by_1_through_9: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install exact numpy`) with:
#   python divisible_by_1_through_9.py

from exact import Exact


def create_model(instance):
    """Find a 10-digit number that uses each digit 0 to 9 exactly once, where the
    number formed by its first n digits is divisible by n, for n = 1 to 10."""
    n = 10  # the number of digits; the problem fixes all data, so the instance is empty

    solver = Exact()

    # Exact identifies its variables by name.
    # digits[i] is the digit at position i, read from left to right
    digits = [f"digit_{i}" for i in range(n)]
    for name in digits:
        solver.addVariable(name, 0, 9)

    # Each of the digits 0 to 9 is used exactly once: is_[i][d] is 1 when position i holds d.
    is_ = [[f"digit_{i}_is_{d}" for d in range(10)] for i in range(n)]
    for i in range(n):
        for name in is_[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in is_[i]], True, 1, True, 1)
        solver.addConstraint([(d, is_[i][d]) for d in range(1, 10)] + [(-1, digits[i])], True, 0, True, 0)
    for d in range(10):
        solver.addConstraint([(1, is_[i][d]) for i in range(n)], True, 1, True, 1)

    # prefix[i] is the number formed by the first i + 1 digits: 10 times the previous one plus the digit.
    prefix = [f"prefix_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(prefix[i], 0, 10 ** (i + 1) - 1)
    solver.addConstraint([(1, prefix[0]), (-1, digits[0])], True, 0, True, 0)
    for i in range(1, n):
        solver.addConstraint([(1, prefix[i]), (-10, prefix[i - 1]), (-1, digits[i])], True, 0, True, 0)

    # The first i + 1 digits form a number divisible by i + 1: prefix[i] = (i + 1) * multiple.
    for i in range(n):
        multiple = f"multiple_{i}"
        solver.addVariable(multiple, 0, (10 ** (i + 1) - 1) // (i + 1))
        solver.addConstraint([(1, prefix[i]), (-(i + 1), multiple)], True, 0, True, 0)

    return solver, {"digits": digits}


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

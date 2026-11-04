# session1_bank_card: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install exact numpy`) with:
#   python session1_bank_card.py

from exact import Exact


def create_model(instance):
    """Find the four-digit PIN abcd of a bank card: no two digits are the same,
    the two-digit number cd is 3 times ab, and the two-digit number da is 2 times bc."""
    # The digits of the PIN, a b c d, each from 0 to 9
    digits = ["a", "b", "c", "d"]

    # Exact identifies its variables by name.
    solver = Exact()
    for name in digits:
        solver.addVariable(name, 0, 9)

    # is_value[name][v] is 1 when that digit is v, and 0 otherwise
    is_value = {name: [f"{name}_is_{v}" for v in range(10)] for name in digits}
    for name in digits:
        for v in range(10):
            solver.addVariable(is_value[name][v], 0, 1)
        # Each digit is exactly one value.
        solver.addConstraint([(1, is_value[name][v]) for v in range(10)], True, 1, True, 1)
        # The digit is the value it takes.
        solver.addConstraint([(v, is_value[name][v]) for v in range(1, 10)] + [(-1, name)],
                             True, 0, True, 0)

    # No two digits are the same: each value is taken by at most one digit.
    for v in range(10):
        solver.addConstraint([(1, is_value[name][v]) for name in digits], False, 0, True, 1)

    # The two-digit number cd is 3 times the two-digit number ab.
    solver.addConstraint([(10, "c"), (1, "d"), (-30, "a"), (-3, "b")], True, 0, True, 0)
    # The two-digit number da is 2 times the two-digit number bc.
    solver.addConstraint([(10, "d"), (1, "a"), (-20, "b"), (-2, "c")], True, 0, True, 0)

    return solver, {name: name for name in digits}


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

# send_more_money: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install exact numpy`) with:
#   python send_more_money.py

from exact import Exact


def create_model(instance):
    """Give each letter a different digit so that SEND + MORE = MONEY holds,
    with no leading zero in SEND, MORE or MONEY."""
    solver = Exact()
    letters = list("sendmory")

    # Exact identifies its variables by name.
    # The digit that each letter stands for, 0 to 9. S and M start a word, so they are not zero.
    for letter in letters:
        solver.addVariable(letter, 1 if letter in "sm" else 0, 9)

    # stands_for[letter][d] is 1 when the letter stands for digit d, and 0 otherwise
    stands_for = {letter: {d: f"{letter}_is_{d}" for d in range(10)} for letter in letters}
    for letter in letters:
        for d in range(10):
            solver.addVariable(stands_for[letter][d], 0, 1)
        # a letter stands for exactly one digit
        solver.addConstraint([(1, stands_for[letter][d]) for d in range(10)], True, 1, True, 1)
        # the letter's digit is the digit it stands for
        solver.addConstraint([(d, stands_for[letter][d]) for d in range(10)] + [(-1, letter)],
                             True, 0, True, 0)
    # every digit is used by at most one letter
    for d in range(10):
        solver.addConstraint([(1, stands_for[letter][d]) for letter in letters], False, 0, True, 1)

    # SEND + MORE = MONEY, each word read as a number
    solver.addConstraint(
        [(1000, "s"), (100, "e"), (10, "n"), (1, "d"), (1000, "m"), (100, "o"), (10, "r"), (1, "e"),
         (-10000, "m"), (-1000, "o"), (-100, "n"), (-10, "e"), (-1, "y")],
        True, 0, True, 0)

    return solver, {name: name for name in letters}


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

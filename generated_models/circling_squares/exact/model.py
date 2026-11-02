# circling_squares: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install exact numpy`) with:
#   python circling_squares.py

from exact import Exact


def create_model(instance):
    """Circling the squares: place a different number in each of ten squares on a circle, so that
    the squares of two adjacent numbers add up to the squares of the two numbers opposite them.
    The numbers in squares A, B, F and G are given."""
    letters = "ABCDEFGHIK"                                   # the squares, in order around the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}              # the numbers the puzzle gives
    largest = 99                                             # no number needs more than two figures
    # Each entry (a, b, c, d): a and b are adjacent squares, and c and d are the squares opposite them.
    pairs = [("A", "B", "F", "G"), ("B", "C", "G", "H"), ("C", "D", "H", "I"),
             ("D", "E", "I", "K"), ("E", "F", "K", "A")]

    solver = Exact()

    # Exact identifies its variables by name.
    # The number in each square is a whole number from 1 to the largest, or the given number.
    for letter in letters:
        if letter in given:
            solver.addVariable(letter, given[letter], given[letter])
        else:
            solver.addVariable(letter, 1, largest)

    # holds[letter][v] is 1 when that square holds the number v, and 0 when not
    holds = {letter: {v: f"{letter}_holds_{v}" for v in range(1, largest + 1)} for letter in letters}
    for letter in letters:
        for v in range(1, largest + 1):
            solver.addVariable(holds[letter][v], 0, 1)

    for letter in letters:
        # Each square holds exactly one number, and that number is the one in the square.
        solver.addConstraint([(1, holds[letter][v]) for v in range(1, largest + 1)], True, 1, True, 1)
        solver.addConstraint([(v, holds[letter][v]) for v in range(1, largest + 1)] + [(-1, letter)],
                             True, 0, True, 0)

    # No number is in two squares, so the numbers are all different.
    for v in range(1, largest + 1):
        solver.addConstraint([(1, holds[letter][v]) for letter in letters], False, 0, True, 1)

    # squares[letter] is the number in that square times itself.
    squares = {letter: f"{letter}_squared" for letter in letters}
    for letter in letters:
        solver.addVariable(squares[letter], 1, largest * largest)
        solver.addMultiplication([letter, letter], True, squares[letter], True, squares[letter])

    # The squares of each adjacent pair add up to the squares of the pair opposite them.
    for a, b, c, d in pairs:
        solver.addConstraint([(1, squares[a]), (1, squares[b]), (-1, squares[c]), (-1, squares[d])],
                             True, 0, True, 0)

    return solver, {letter: letter for letter in letters}


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

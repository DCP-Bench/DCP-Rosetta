# circling_squares: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install ortools`) with:
#   python circling_squares.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Circling the squares: place a different number in each of the ten squares of a circle,
    so that two adjacent squares have the same sum of squares as the two squares
    diametrically opposite them."""
    model = cp_model.CpModel()

    # the squares in order around the circle
    names = "ABCDEFGHIK"
    # the numbers given in the puzzle, by square
    given = {"A": 16, "B": 2, "F": 8, "G": 14}
    # x[j] is the number in square j; each number has at most two figures, so it is from 1 to 99
    x = [model.new_int_var(given.get(name, 1), given.get(name, 99), name) for name in names]

    # Each square holds a different number.
    model.add_all_different(x)

    # squares[name] is the square of the number in that square.
    squares = {}
    for value, name in zip(x, names):
        square = model.new_int_var(1, 99 * 99, f"{name}_squared")
        model.add_multiplication_equality(square, [value, value])
        squares[name] = square

    # The five pairs of adjacent squares, each against the two squares opposite them.
    for first, second, third, fourth in (
        ("A", "B", "F", "G"),
        ("B", "C", "G", "H"),
        ("C", "D", "H", "I"),
        ("D", "E", "I", "K"),
        ("E", "F", "K", "A"),
    ):
        model.add(
            squares[first] + squares[second] == squares[third] + squares[fourth]
        )

    return model, {name: var for name, var in zip(names, x)}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

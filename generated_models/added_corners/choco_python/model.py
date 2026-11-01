# added_corners: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install pychoco numpy`) with:
#   python added_corners.py

from pychoco.model import Model


def create_model(instance):
    """Enter the digits 1 to 8 in the circles and squares of a ring, one digit per
    cell, so that the number in each square is the sum of the two circles beside it."""
    model = Model()

    # The digit in each cell. Cells are numbered like the words of a book, left to
    # right and top to bottom, skipping the empty middle.
    positions = [model.intvar(1, 8, name=f"p{i}") for i in range(8)]

    # Each digit is used once.
    model.all_different(positions).post()

    # Cells 0, 2, 5 and 7 are circles; cells 1, 3, 4 and 6 are squares. The top square
    # (cell 1) sits between circles 0 and 2, the left square (3) between 0 and 5, the
    # right square (4) between 2 and 7, and the bottom square (6) between 5 and 7.
    for square, first, second in ((1, 0, 2), (3, 0, 5), (4, 2, 7), (6, 5, 7)):
        model.scalar(
            [positions[square], positions[first], positions[second]],
            [1, -1, -1], "=", 0,
        ).post()

    return model, {"positions": positions}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

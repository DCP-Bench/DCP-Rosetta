# added_corners: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/added_corners.html
# Run it (after `pip install ortools`) with:
#   python added_corners.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Enter the digits 1 through 8 in the circles and squares of a ring such that
    the number in each square is equal to the sum of the adjoining circles."""
    model = cp_model.CpModel()

    # positions[i] is the digit in cell i, numbering the cells left to right and top
    # to bottom, skipping the empty middle.
    positions = [model.new_int_var(1, 8, f"position_{i}") for i in range(8)]
    # a to h are the digits in cells 0 to 7.
    a, b, c, d, e, f, g, h = positions

    # Each digit is used once.
    model.add_all_different(positions)
    # Cells 0, 2, 5 and 7 are circles; cells 1, 3, 4 and 6 are squares.
    # Each square is the sum of the two circles next to it.
    model.add(b == a + c)  # top square
    model.add(d == a + f)  # left square
    model.add(e == c + h)  # right square
    model.add(g == f + h)  # bottom square

    return model, {"positions": positions}


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

# session5_hardy_1729_square: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install ortools`) with:
#   python session5_hardy_1729_square.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two."""
    model = cp_model.CpModel()

    # a, b, c, d are the four numbers, each between 1 and 100
    numbers = [model.new_int_var(1, 100, name) for name in "abcd"]
    a, b, c, d = numbers

    # squares[i] is the square of numbers[i]
    squares = []
    for value, name in zip(numbers, "abcd"):
        square = model.new_int_var(1, 100 ** 2, f"{name}_squared")
        model.add_multiplication_equality(square, [value, value])
        squares.append(square)

    # a^2 + b^2 = c^2 + d^2
    model.add(squares[0] + squares[1] == squares[2] + squares[3])

    # The four numbers are different.
    model.add_all_different(numbers)

    return model, {"a": a, "b": b, "c": c, "d": d}


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

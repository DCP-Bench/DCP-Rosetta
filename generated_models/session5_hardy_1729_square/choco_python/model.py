# session5_hardy_1729_square: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install pychoco numpy`) with:
#   python session5_hardy_1729_square.py

from pychoco.model import Model


def create_model(instance):
    """Find four different numbers between 1 and 100 such that the sum of the squares
    of the first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    model = Model()

    # numbers[0..3] are a, b, c, d, each from 1 to 100
    numbers = [model.intvar(1, 100, name=name) for name in "abcd"]
    a, b, c, d = numbers

    # squares[k] is the square of numbers[k], at most 100^2
    squares = [model.intvar(1, 100 ** 2, name=name + "_squared") for name in "abcd"]
    for number, square in zip(numbers, squares):
        model.square(square, number).post()

    # a^2 + b^2 = c^2 + d^2
    model.scalar(squares, [1, 1, -1, -1], "=", 0).post()

    # The four numbers are different.
    model.all_different(numbers).post()

    return model, {"a": a, "b": b, "c": c, "d": d}, None


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

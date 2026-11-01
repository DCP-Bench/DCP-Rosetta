# circling_squares: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install pychoco numpy`) with:
#   python circling_squares.py

from pychoco.model import Model


def create_model(instance):
    """Circling the squares: place a different number in each of ten squares on a circle, so that
    for any two adjacent squares the sum of their squares equals the sum of the squares of the two
    squares opposite them. Four of the numbers are given."""
    names = "ABCDEFGHIK"                        # the squares, in order round the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}  # the numbers placed as examples
    n = len(names)                              # the number of squares

    model = Model()

    # numbers[k] is the number in square names[k]; no number needs more than two figures
    numbers = [model.intvar(given.get(name, 1), given.get(name, 99), name=name) for name in names]
    # squares[k] is the square of numbers[k]
    squares = [model.intvar(1, 99 * 99, name=f"square_{name}") for name in names]
    for number, square in zip(numbers, squares):
        model.square(square, number).post()

    # Every square holds a different number.
    model.all_different(numbers).post()

    # Two adjacent squares have the same sum of squares as the two squares opposite them.
    for k in range(n // 2):
        opposite = (k + n // 2) % n
        model.scalar(
            [squares[k], squares[k + 1], squares[opposite], squares[(opposite + 1) % n]],
            [1, 1, -1, -1], "=", 0,
        ).post()

    return model, {name: number for name, number in zip(names, numbers)}, None


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

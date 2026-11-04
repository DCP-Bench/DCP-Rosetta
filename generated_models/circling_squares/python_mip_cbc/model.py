# circling_squares: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install mip numpy`) with:
#   python circling_squares.py

import mip


def create_model(instance):
    """Place a different whole number from 0 to 99 in each of ten squares, named A, B, C, D, E, F, G,
    H, I and K and arranged in a circle, so that the sum of the squares of any two adjacent numbers
    equals the sum of the squares of the two numbers diametrically opposite them. The numbers in
    squares A, B, F and G are given."""
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # the squares in order around the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}  # the numbers given in the puzzle
    numbers = range(100)                        # no fractions, and no number needs more than two figures
    n_squares = len(names)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # p[i][v] is 1 when square i holds the number v, and 0 when not
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in numbers] for i in range(n_squares)]
    # x[i] is the number in square i; a given number fixes its square
    x = [
        model.add_var(name, var_type=mip.INTEGER,
                      lb=given.get(name, min(numbers)), ub=given.get(name, max(numbers)))
        for name in names
    ]
    # sq[i] is the square of the number in square i
    sq = [model.add_var(f"sq_{i}", var_type=mip.INTEGER, lb=0, ub=max(numbers) ** 2)
          for i in range(n_squares)]

    # Each square holds exactly one number.
    for i in range(n_squares):
        model += mip.xsum(p[i]) == 1

    # The number and its square in each square are the ones chosen for it.
    for i in range(n_squares):
        model += x[i] == mip.xsum(v * p[i][v] for v in numbers)
        model += sq[i] == mip.xsum(v * v * p[i][v] for v in numbers)

    # Different squares hold different numbers.
    for v in numbers:
        model += mip.xsum(p[i][v] for i in range(n_squares)) <= 1

    # Each pair of adjacent squares has the same sum of squares as the two squares diametrically opposite them.
    for i in range(n_squares):
        model += sq[i] + sq[(i + 1) % n_squares] == sq[(i + 5) % n_squares] + sq[(i + 6) % n_squares]

    return model, dict(zip(names, x))


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

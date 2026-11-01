# dudeney_numbers: a Choco-solver (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

from pychoco.model import Model


def create_model(instance):
    """Find a number larger than 1, with at most n digits, that is a perfect cube
    whose digits add up to its cube root."""
    n = instance["n"]  # the most digits the number may have
    largest = 10 ** n - 1  # the largest number with n digits

    model = Model()

    # digits[i] is the i-th digit of the number, most significant first
    digits = [model.intvar(0, 9, name=f"digit_{i}") for i in range(n)]
    # the number
    number = model.intvar(0, largest, name="number", bounded_domain=True)
    # the cube root of the number; the digits add up to at most 9 per digit
    cube_root = model.intvar(1, 9 * n, name="cube_root")

    # The number is written with these digits.
    model.scalar(digits, [10 ** (n - i - 1) for i in range(n)], "=", number).post()

    # The cube root is the sum of the digits.
    model.sum(digits, "=", cube_root).post()

    # The number is the cube of its cube root. Only roots whose cube has at most n digits qualify.
    cubes = [(r, r ** 3) for r in range(1, 9 * n + 1) if r ** 3 <= largest]
    model.table([cube_root, number], cubes).post()

    # The number is larger than 1.
    model.arithm(number, ">", 1).post()

    return model, {"number": number}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
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

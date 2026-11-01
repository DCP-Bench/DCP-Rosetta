# dudeney_numbers: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install ortools`):
#   python dudeney_numbers.py dudeney_numbers.json

from ortools.sat.python import cp_model


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that
    the sum of its digits is equal to the cube root of the number. Find such a
    number that is larger than 1."""
    n_digits = instance["n"]  # the number of digits of the number

    model = cp_model.CpModel()

    # digits[i] is the i-th digit of the number, from the most significant
    digits = [model.new_int_var(0, 9, f"digit_{i}") for i in range(n_digits)]
    # number is the Dudeney number, larger than 1
    number = model.new_int_var(2, 10**n_digits - 1, "number")
    # cube_root is the cube root of the number; the largest possible digit sum is 9 * n_digits
    cube_root = model.new_int_var(1, 9 * n_digits, "cube_root")
    # squared is cube_root * cube_root, the step on the way to the cube
    squared = model.new_int_var(1, (9 * n_digits) ** 2, "squared")

    # The number is the cube of cube_root.
    model.add_multiplication_equality(squared, [cube_root, cube_root])
    model.add_multiplication_equality(number, [squared, cube_root])
    # The digits sum to the cube root.
    model.add(cube_root == sum(digits))
    # The digits spell out the number.
    model.add(number == sum(d * 10 ** (n_digits - i - 1) for i, d in enumerate(digits)))

    return model, {"number": number}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

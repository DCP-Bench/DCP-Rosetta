# dudeney_numbers: an Exact (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

from exact import Exact


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that the
    sum of its digits equals the cube root of the number. Find one larger than 1
    with at most n digits."""
    n_digits = instance["n"]  # the number has at most this many digits

    solver = Exact()

    # Exact identifies its variables by name.
    # digits[i] is the i-th digit of the number from the left; a shorter number has leading zeros
    digits = [f"digit_{i}" for i in range(n_digits)]
    for name in digits:
        solver.addVariable(name, 0, 9)

    # The Dudeney number, larger than 1
    solver.addVariable("number", 2, 10 ** n_digits - 1)
    # cube_root is the cube root of the number. Each digit is at most 9, so the digit sum is at most 9 * n_digits.
    solver.addVariable("cube_root", 1, 9 * n_digits)
    # square is cube_root * cube_root, the step on the way to the cube
    solver.addVariable("square", 1, (9 * n_digits) ** 2)

    # The number is the cube of the cube root.
    solver.addMultiplication(["cube_root", "cube_root"], True, "square", True, "square")
    solver.addMultiplication(["square", "cube_root"], True, "number", True, "number")
    # The digits add up to the cube root.
    solver.addConstraint([(1, name) for name in digits] + [(-1, "cube_root")], True, 0, True, 0)
    # The digits spell out the number.
    solver.addConstraint([(10 ** (n_digits - 1 - i), digits[i]) for i in range(n_digits)]
                         + [(-1, "number")], True, 0, True, 0)

    return solver, {"number": "number"}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

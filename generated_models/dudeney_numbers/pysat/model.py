# dudeney_numbers: a PySAT (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that the sum of its
    digits is equal to the cube root of the number. Find such a number that is larger than 1
    and has at most n digits."""
    n = instance["n"]  # the most digits the number may have

    pool = IDPool()

    # number_digits[i] is the i-th digit of the number, from the most significant (leading zeros allowed)
    number_digits = [Integer(f"digit{i}", 0, 9, vpool=pool) for i in range(n)]
    # cube_root is the cube root of the number. It is the digit sum, which is at most 9 * n.
    cube_root = Integer("cube_root", 1, 9 * n, vpool=pool)
    # number is the Dudeney number: larger than 1, with at most n digits
    number = Integer("number", 2, min(10 ** n - 1, (9 * n) ** 3), encoding="coupled", vpool=pool)

    engine = IntegerEngine(vars=number_digits + [cube_root, number], vpool=pool)

    # The cube root is the sum of the digits.
    engine.add_linear(cube_root == sum(number_digits))

    cnf = engine.clausify()

    # The number is the cube of cube_root, and its digits are the digits of that cube. For each
    # possible root, the cube and its digits are fixed, and the root selects that row.
    for root in range(1, 9 * n + 1):
        cube = root ** 3
        if cube < 2 or cube >= 10 ** n:
            # the cube is 1 or has more than n digits, so it cannot be the number
            cnf.append([-cube_root.equals(root)])
            continue
        cnf.append([-cube_root.equals(root), number.equals(cube)])
        for i, digit in enumerate(str(cube).zfill(n)):
            cnf.append([-cube_root.equals(root), number_digits[i].equals(int(digit))])

    return cnf, {"number": number}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

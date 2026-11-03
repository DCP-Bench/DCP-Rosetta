# dudeney_numbers: a SCIP (Python) model from DCP Rosetta.
# Download the `dudeney_numbers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/dudeney_numbers.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python dudeney_numbers.py dudeney_numbers.json

from pyscipopt import Model, quicksum


def integer_cube_root(x):
    """The largest integer k with k**3 <= x, for x >= 0."""
    k = round(x ** (1 / 3))  # a float estimate, corrected below for large x
    while k**3 > x:
        k -= 1
    while (k + 1) ** 3 <= x:
        k += 1
    return k


def create_model(instance):
    """A Dudeney number is a positive integer that is a perfect cube such that the
    sum of its digits equals the cube root of the number. Find such a number
    larger than 1 that has at most n digits."""
    n = instance["n"]  # the most digits the number may have

    model = Model("dudeney_numbers")

    # k is the cube root of the number, so number = k**3. The number is larger
    # than 1, so k >= 2. It has at most n digits, so k**3 <= 10**n - 1, which gives
    # the upper bound on k.
    k = model.addVar("k", vtype="I", lb=2, ub=integer_cube_root(10**n - 1))

    # digits[i] is the digit in place 10**i of the number, from 0 (units) upward.
    # Leading zeros are allowed, so a number with fewer digits fits in n places.
    # Each digit is between 0 and 9 because the number is written in base 10.
    digits = [model.addVar(f"digit_{i}", vtype="I", lb=0, ub=9) for i in range(n)]

    # The number is the sum of its digits weighted by their places.
    number = quicksum(10**i * d for i, d in enumerate(digits))

    # The number is a perfect cube: it is the cube of its root k.
    model.addCons(number == k**3)

    # The sum of the digits of the number equals its cube root k.
    model.addCons(quicksum(digits) == k)

    # The problem asks for a number, so there is no objective.
    return model, {"number": number}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

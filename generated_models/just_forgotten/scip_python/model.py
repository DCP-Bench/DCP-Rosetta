# just_forgotten: a SCIP (Python) model from DCP Rosetta.
# Download the `just_forgotten.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/just_forgotten.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python just_forgotten.py just_forgotten.json

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Joe's account number x is a list of the digits 0 to n-1, each used once, in
    some order. Each set he tried is a guess of n digits in which exactly
    num_correct_digits of the digits are in the same position as in x. Find x."""
    sets = instance["sets"]                   # sets[k][i]: the digit in position i of guess k
    correct = instance["num_correct_digits"]  # how many digits of every guess are in their correct position
    n = len(sets[0])                          # the number of digits: the length of each guess

    model = Model("just_forgotten")

    # b[i, v] is 1 when digit v is in position i of the account number, and 0 when not
    b = model.addMatrixVar((n, n), vtype="B", name="b")

    # Each position holds exactly one digit. SCIP has no all-different, so a permutation
    # is written as a 0/1 matrix with exactly one 1 in every row and column.
    model.addMatrixCons(b.sum(axis=1) == 1)
    # Each digit sits in exactly one position: the digits 0 to n-1 are all used, once each.
    model.addMatrixCons(b.sum(axis=0) == 1)

    # For each set of guesses: the digits in their correct position are exactly
    # num_correct_digits. same[i, v] is 1 when the guess has digit v in position i, so
    # the sum counts the positions where the guess and the account number agree.
    for guess in sets:
        same = np.eye(n)[guess]
        model.addCons((same * b).sum() == correct)

    # No objective: any account number that matches every set is the answer.

    # x[i] is the digit in position i of the account number: the v with b[i, v] = 1.
    x = (b * np.arange(n)).sum(axis=1)

    return model, {"x": x}


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

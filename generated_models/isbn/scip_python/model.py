# isbn: a SCIP (Python) model from DCP Rosetta.
# Download the `isbn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/isbn.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python isbn.py isbn.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Fill in the unknown digits of a 13-digit ISBN so that it is a valid ISBN-13:
    it starts with 978 or 979, and its digits weighted 1, 3, 1, 3, ... (starting
    with 1) sum to a multiple of 10, which makes the last digit the check digit."""
    isbn_init = instance["isbn_init"]  # isbn_init[i]: the i-th digit of the ISBN, or -1 when that digit is unknown
    n = len(isbn_init)                 # the number of digits, 13, from the data

    model = Model("isbn")

    # d[i] is the i-th digit of the ISBN, a whole number from 0 to 9.
    # A digit given in the instance is fixed to its value.
    d = []
    for i, given in enumerate(isbn_init):
        if given >= 0:
            d.append(model.addVar(f"d_{i}", vtype="I", lb=given, ub=given))
        else:
            d.append(model.addVar(f"d_{i}", vtype="I", lb=0, ub=9))

    # The ISBN starts with 978 or 979: the first digit is 9, the second is 7,
    # and the third is 8 or 9 (its upper bound 9 already holds from the digit range).
    model.addCons(d[0] == 9)
    model.addCons(d[1] == 7)
    model.addCons(d[2] >= 8)

    # The weights are 1 and 3 alternately, starting with 1, as the statement gives them
    # for the first 12 digits; the 13th (check) digit has weight 1 as well, since it is at an even position.
    weights = [1 if i % 2 == 0 else 3 for i in range(n)]

    # k is the weighted digit sum divided by 10. With digits 0 to 9 the sum is at most
    # 9 * sum(weights), so k is at most that divided by 10.
    k = model.addVar("k", vtype="I", lb=0, ub=9 * sum(weights) // 10)

    # Check digit rule: the weighted sum of all 13 digits is a multiple of 10. For the first
    # 12 digits with sum S, the statement's check digit is (10 - S % 10) % 10, and that is
    # exactly the digit making S + check digit a multiple of 10.
    model.addCons(quicksum(w * di for w, di in zip(weights, d)) == 10 * k)

    # No objective: any valid ISBN-13 that fits the given digits is a solution.
    return model, {"isbn": d}


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

# divisible_by_1_through_9: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python divisible_by_1_through_9.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Find a 10-digit number that uses each of the digits 0 to 9 exactly once,
    and where the number formed by its first n digits is divisible by n, for
    every n from 1 to 10.

    The instance file is empty ([]): the statement fixes all the data, so
    create_model does not read its argument.

    Output digits: the ten digits of the number, read from left to right.
    """
    model = Model("divisible_by_1_through_9")

    # b[i, v] is 1 when position i of the number (0 is the leftmost) holds the
    # digit v, and 0 when not. There are 10 positions and the digits 0 to 9,
    # both fixed by the statement.
    b = model.addMatrixVar((10, 10), vtype="B", name="b")

    # Each position holds exactly one digit.
    model.addMatrixCons(b.sum(axis=1) == 1)

    # Each digit from 0 to 9 is used exactly once. SCIP has no all-different
    # constraint, so each digit appearing once is written as a column sum of 1.
    model.addMatrixCons(b.sum(axis=0) == 1)

    # digit[i] is the digit at position i: the value v whose b[i, v] is 1.
    digit = [quicksum(v * b[i, v] for v in range(10)) for i in range(10)]

    # A 10-digit number has no leading zero.
    model.addCons(b[0, 0] == 0)

    # The first n digits form the number prefix, which must be divisible by n:
    # prefix == n * quotient for a whole number quotient. Divisibility by 1
    # always holds, so the rule is checked from n = 2 to n = 10.
    for n in range(2, 11):
        prefix = quicksum(10 ** (n - 1 - i) * digit[i] for i in range(n))

        # quotient is the whole number prefix / n. Every digit is at most 9, so
        # the first n digits form at most 10**n - 1 (n nines), which bounds the
        # quotient by (10**n - 1) // n.
        quotient = model.addVar(f"quotient_{n}", vtype="I", lb=0, ub=(10**n - 1) // n)

        model.addCons(prefix == n * quotient)

    return model, {"digits": digit}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

# cur_num: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python cur_num.py

from pyscipopt import Model


def create_model(instance):
    """Find a number n between 1 and 10000, other than 48, such that n + 1 is a
    square number and n / 2 + 1 is also a square number. The instance file is
    empty ([]), so the statement fixes all the data and nothing is read from
    the instance argument."""
    model = Model("cur_num")

    # n is the peculiar number the statement asks for, between 1 and 10000
    # (the bounds come from the statement's range).
    n = model.addVar("n", vtype="I", lb=1, ub=10000)

    # a is the square root of n + 1. Since n + 1 <= 10001 and 101 * 101 = 10201 > 10001,
    # a is at most 100 (a derived bound).
    a = model.addVar("a", vtype="I", lb=1, ub=100)

    # b is the square root of n / 2 + 1. Since n + 2 <= 10002 and 71 * 71 * 2 = 10082 > 10002,
    # b is at most 70 (a derived bound).
    b = model.addVar("b", vtype="I", lb=1, ub=70)

    # n + 1 is a square number: n + 1 = a * a, written with the power operator, which SCIP
    # accepts in a constraint on an integer variable.
    model.addCons(n + 1 == a**2)

    # n / 2 + 1 is a square number, written without halving n: n / 2 + 1 = b * b gives
    # n + 2 = 2 * b * b. The right side is even, so this also forces n to be even.
    model.addCons(n + 2 == 2 * b**2)

    # The statement asks for another number, so 48 is excluded. SCIP has no != on
    # integers, so one binary d picks the side: n <= 47 when d = 1, and n >= 49 when d = 0.
    d = model.addVar("d", vtype="B")
    model.addConsIndicator(n <= 47, binvar=d)
    model.addConsIndicator(n >= 49, binvar=d, activeone=False)

    # Satisfaction problem: no objective, so any n meeting the constraints is an answer.
    return model, {"peculiar": n}


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

# session5_hardy_1729_square: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python session5_hardy_1729_square.py

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Find four different whole numbers from 1 to 100 such that the sum of the squares
    of the first two equals the sum of the squares of the other two, a^2 + b^2 = c^2 + d^2,
    and report them as (a, b, c, d).

    The instance file is empty ([]): the statement fixes every number, so nothing is
    read from `instance`.
    """
    # The statement fixes the range: the whole numbers 1 to 100.
    values = np.arange(1, 101)  # column k stands for the number values[k] = k + 1

    model = Model("hardy_1729_square")

    # x[i, k] is 1 when the i-th of a, b, c, d (in that order) is the number k + 1,
    # and 0 when not. SCIP has no all-different constraint and no "!=", so each
    # number is one-hot over the 100 values and the four numbers are kept apart below.
    x = model.addMatrixVar((4, 100), vtype="B", name="x")

    # Each of a, b, c, d is exactly one number from 1 to 100.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # The four numbers are different: each value 1 to 100 is picked by at most one of them.
    model.addMatrixCons(x.sum(axis=0) <= 1)

    # The numbers themselves and their squares, as linear expressions of the one-hot choices.
    number = x @ values          # number[i]: the i-th number picked
    square = x @ (values ** 2)   # square[i]: its square

    # The sum of the squares of a and b equals the sum of the squares of c and d.
    model.addCons(square[0] + square[1] == square[2] + square[3])

    # There is no objective: the problem asks for any solution.
    return model, {"a": number[0], "b": number[1], "c": number[2], "d": number[3]}


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

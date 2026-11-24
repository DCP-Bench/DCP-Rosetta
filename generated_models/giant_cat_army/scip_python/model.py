# giant_cat_army: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python giant_cat_army.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Giant cat army: the list starts as [0]. Each step appends one number to it:
    the last number plus 5, the last number plus 7, or the square root of the last
    number (only when that root is an integer). The finished list has 24 numbers,
    starts with 0, ends with 14, and contains 2 and then 10 before that 14 (other
    numbers may lie between them). All numbers are distinct, integers, and at most 60.

    The instance file is empty ([]): the statement fixes every number, so the
    instance argument is not read.
    """
    length = 24         # the list has 24 numbers, at positions 0 to 23
    largest = 60        # every number is at most 60, so it is one of the values 0 to 60
    steps = length - 1  # each step appends one number to the list

    model = Model("giant_cat_army")

    # V[i, k] is 1 when the number at position i of the list is k, and 0 otherwise.
    # Each position holds exactly one value. SCIP has no all-different constraint,
    # so distinctness is written as "each value is used at most once" over the positions.
    V = model.addMatrixVar((length, largest + 1), vtype="B", name="V")
    model.addMatrixCons(V.sum(axis=1) == 1)  # each position holds exactly one value
    model.addMatrixCons(V.sum(axis=0) <= 1)  # each value is in the list at most once

    # value[i] is the number at position i, read off the one-hot row V[i, :].
    # It is an expression, not a variable, so the outputs are these expressions.
    value = [quicksum(k * V[i, k] for k in range(largest + 1)) for i in range(length)]

    # The list starts at 0 and ends with 14.
    model.addCons(V[0, 0] == 1)
    model.addCons(V[length - 1, 14] == 1)

    # 2 and 10 each appear in the list (distinctness allows at most one of each).
    model.addMatrixCons(V[:, [2, 10]].sum(axis=0) == 1)

    # 2 comes before 10: the position of 2 is less than the position of 10.
    # SCIP has no strict <, so the position of 2 plus one is at most the position of 10.
    position_of_2 = quicksum(i * V[i, 2] for i in range(length))
    position_of_10 = quicksum(i * V[i, 10] for i in range(length))
    model.addCons(position_of_2 + 1 <= position_of_10)

    # op[i, 0] is 1 when step i adds 5, op[i, 1] when it adds 7, and op[i, 2] when it
    # takes the square root. Each step uses exactly one operation.
    op = model.addMatrixVar((steps, 3), vtype="B", name="op")
    model.addMatrixCons(op.sum(axis=1) == 1)

    for i in range(steps):
        # Adding 5 or 7: the next number is this number plus 5 (or plus 7).
        # addConsIndicator takes only <= or >=, so each equality is two indicators
        # on the same binary.
        model.addConsIndicator(value[i + 1] - value[i] <= 5, binvar=op[i, 0])
        model.addConsIndicator(value[i + 1] - value[i] >= 5, binvar=op[i, 0])
        model.addConsIndicator(value[i + 1] - value[i] <= 7, binvar=op[i, 1])
        model.addConsIndicator(value[i + 1] - value[i] >= 7, binvar=op[i, 1])

        # Taking the square root: the next number r is the root, so this number is r * r.
        # The next number is at most 7, since 8 * 8 = 64 is above 60. The sum runs over
        # the roots 0 to 7 only, and the constraint after it rules out larger roots.
        # The square coefficients stay at most 49: with squares up to 3600, SCIP 10.0.2
        # reported this model infeasible although a list meeting every rule exists.
        # Two indicators make the equality.
        squares = quicksum(r * r * V[i + 1, r] for r in range(8))
        model.addCons(quicksum(V[i + 1, r] for r in range(8, largest + 1)) <= 1 - op[i, 2])
        model.addConsIndicator(value[i] - squares <= 0, binvar=op[i, 2])
        model.addConsIndicator(value[i] - squares >= 0, binvar=op[i, 2])

    # The problem has no objective: any list that meets the rules above is an answer.
    return model, {"x": value}


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

# age_changing: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python age_changing.py

from pyscipopt import Model

# The four operations, each as a linear relation  a * next == b * current + c
# between the age before the step (current) and after it (next):
#   +2: next = current + 2   (a=1, b=1, c=2)
#   /8: 8 * next = current   (a=8, b=1, c=0): the division is exact, so the
#       age before it must be a multiple of 8 (an assumption: the statement
#       does not say what a fraction of a year would be)
#   -3: next = current - 3   (a=1, b=1, c=-3)
#   *7: next = 7 * current   (a=1, b=7, c=0)
STEPS = [(1, 1, 2), (8, 1, 0), (1, 1, -3), (1, 7, 0)]


def create_model(instance):
    """Two ages, my age m and my husband's age h, linked by four operations.

    Starting from my age and applying +2, /8, -3 and *7, each once and in some
    order, gives his age. Starting from his age and applying the same four
    operations in a different order gives mine. Find both ages.

    The instance file is empty ([]): the statement fixes all the data, so the
    instance argument is not read.
    """
    model = Model("age_changing")

    # m is my age and h is his, in whole years. The statement does not bound
    # them: 0 to 200 is an assumption (a human age), and it cuts no answer,
    # since the answers are below 100.
    m = model.addVar(name="m", vtype="I", lb=0, ub=200)
    h = model.addVar(name="h", vtype="I", lb=0, ub=200)

    def chain(first, last, label):
        # values[k] is the age after k steps: values[0] is the start and
        # values[4] the end. The bounds -21 and 1414 are derived from the steps:
        # the largest value from an age of at most 200 is (200 + 2) * 7 = 1414,
        # since +2 and *7 are the only increasing steps and each is used once;
        # the smallest from an age of 0 is -21 = (0 - 3) * 7, the lowest reached
        # from an age of 0 over all 24 orders of the steps.
        values = [first]
        for k in (1, 2, 3):
            values.append(model.addVar(name=f"{label}_{k}", vtype="I", lb=-21, ub=1414))
        values.append(last)

        # step[o, p] is 1 when operation o (a row, in the order of STEPS) is the
        # p-th step (a column) of this chain.
        step = model.addMatrixVar((4, 4), vtype="B", name=f"{label}_step")

        # Each operation is used exactly once (rows) and each step position holds
        # exactly one operation (columns).
        model.addMatrixCons(step.sum(axis=1) == 1)
        model.addMatrixCons(step.sum(axis=0) == 1)

        # If operation o is the p-th step, the age after it follows from the age
        # before it. SCIP's indicator takes only <= or >=, so each equality is
        # two indicators on the same binary.
        for p in range(4):
            for o, (a, b, c) in enumerate(STEPS):
                model.addConsIndicator(a * values[p + 1] - b * values[p] <= c, binvar=step[o, p])
                model.addConsIndicator(a * values[p + 1] - b * values[p] >= c, binvar=step[o, p])
        return step

    # My age m, through the steps in one order, gives his age h.
    mine_order = chain(m, h, "mine_to_his")
    # His age h, through the steps in another order, gives my age m.
    his_order = chain(h, m, "his_to_mine")

    # The two orders must differ, so they cannot agree at all four steps. same[o, p]
    # is 1 when both orders have operation o at step p; addConsAnd sets it in both
    # directions, so it is 1 exactly when they agree there.
    same = model.addMatrixVar((4, 4), vtype="B", name="same_operation")
    for o in range(4):
        for p in range(4):
            model.addConsAnd([mine_order[o, p], his_order[o, p]], same[o, p])
    # The agreements at the four steps add up to at most 3: a different order
    # disagrees at some step.
    model.addCons(same.sum() <= 3)

    # No objective: the problem asks for the two ages, not for an optimum.
    return model, {"h": h, "m": m}


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

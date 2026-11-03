# giant_cat_army: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Run it (after `pip install mip numpy`) with:
#   python giant_cat_army.py

import mip

# The list has 24 numbers.
LENGTH = 24
# Every number on the list is at most 60.
MAX_VALUE = 60
# Square roots that can be taken: 1 to 7, whose squares are the perfect squares 1 to 49.
# The root of 0 would repeat the start of the list, so it is left out.
ROOTS = range(1, 8)


def _next_values(v):
    """The numbers a step can reach from v: add 5, add 7, or take the square root of a perfect square."""
    reached = [v + 5, v + 7]
    root = int(v ** 0.5)
    if root >= 1 and root * root == v:
        reached.append(root)
    return [w for w in reached if w <= MAX_VALUE]


def create_model(instance):
    """Build a list of 24 distinct whole numbers, each at most 60. The list starts with
    0 and ends with 14. Each step adds 5, adds 7, or takes the square root of a perfect
    square. The list holds 2, 10 and 14 in that order, with other numbers allowed between."""
    model = mip.Model(solver_name="CBC")
    # Every value a number on the list can take.
    values = range(MAX_VALUE + 1)

    # p[i][v] is 1 when the i-th number on the list is v, and 0 when not.
    p = [[model.add_var(f"p_{i}_{v}", var_type=mip.BINARY) for v in values] for i in range(LENGTH)]
    # x[i] is the i-th number on the list.
    x = [mip.xsum(v * p[i][v] for v in values) for i in range(LENGTH)]

    # Each position holds exactly one number.
    for i in range(LENGTH):
        model.add_constr(mip.xsum(p[i]) == 1)

    # The list starts with 0 and ends with 14.
    model.add_constr(p[0][0] == 1)
    model.add_constr(p[LENGTH - 1][14] == 1)

    # No number appears twice on the list.
    for v in values:
        model.add_constr(mip.xsum(p[i][v] for i in range(LENGTH)) <= 1)

    # Each step is an allowed step: a number at position i is followed by one it can reach,
    # and a number at position i + 1 is preceded by one that reaches it.
    for i in range(LENGTH - 1):
        for v in values:
            model.add_constr(p[i][v] <= mip.xsum(p[i + 1][w] for w in _next_values(v)))
        for w in values:
            before = [v for v in values if w in _next_values(v)]
            model.add_constr(p[i + 1][w] <= mip.xsum(p[i][v] for v in before))

    # The position of number v on the list.
    def pos(v):
        return mip.xsum(i * p[i][v] for i in range(LENGTH))

    # Each of 2, 10 and 14 appears once on the list.
    for v in (2, 10, 14):
        model.add_constr(mip.xsum(p[i][v] for i in range(LENGTH)) == 1)
    # 2 comes before 10, and 10 comes before 14.
    model.add_constr(pos(2) + 1 <= pos(10))
    model.add_constr(pos(10) + 1 <= pos(14))

    # No objective: any list that meets the conditions answers the question.
    return model, {"x": x}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

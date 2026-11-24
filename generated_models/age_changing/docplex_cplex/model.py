# age_changing: a CPLEX (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install docplex cplex`; the CPLEX that comes with pip allows models
# up to 1000 variables and 1000 constraints) with:
#   python age_changing.py

from docplex.mp.model import Model


def create_model(instance):
    """Age changing (Enigma 1224): applying the four operations +2, /8, -3 and *7 in some order to my
    age gives my husband's age, and applying the same four operations in a different order to his
    age gives mine. Both ages are between 16 and 120, and every intermediate result is a positive
    integer, so a division by 8 is exact. What are our two ages?"""
    n = 4                          # number of operations (puzzle constant)
    age_low, age_high = 16, 120    # both ages lie between 16 and 120
    low, high = 1, 1000            # intermediate results are positive integers; none exceeds (120 + 2) * 7 = 854, the most +2 then *7 can give
    ops = range(n)                 # 0: +2, 1: /8, 2: -3, 3: *7
    steps = range(n)

    model = Model("age_changing")

    m = model.integer_var(age_low, age_high, name="m")  # my age
    h = model.integer_var(age_low, age_high, name="h")  # my husband's age

    # Values after each operation, starting from my age (hlist) and from his age (mlist).
    hlist = [model.integer_var(low, high, name=f"hlist_{i}") for i in range(n + 1)]
    mlist = [model.integer_var(low, high, name=f"mlist_{i}") for i in range(n + 1)]

    # order1[i, k] = 1 when operation k is applied at step i to my age; order2 likewise to his
    # age. Each is a permutation: every step applies one operation and every operation is used.
    order1 = {(i, k): model.binary_var(name=f"order1_{i}_{k}") for i in steps for k in ops}
    order2 = {(i, k): model.binary_var(name=f"order2_{i}_{k}") for i in steps for k in ops}
    for order in (order1, order2):
        for i in steps:
            model.add_constraint(model.sum(order[i, k] for k in ops) == 1)
        for k in ops:
            model.add_constraint(model.sum(order[i, k] for i in steps) == 1)

    # The two orders differ: at most n - 1 steps apply the same operation in both. same[i, k]
    # is at least 1 when both orders apply operation k at step i.
    same = {(i, k): model.binary_var(name=f"same_{i}_{k}") for i in steps for k in ops}
    model.add_constraints(same[i, k] >= order1[i, k] + order2[i, k] - 1 for i in steps for k in ops)
    model.add_constraint(model.sum(same.values()) <= n - 1)

    # Starting from my age, the operations give my husband's age.
    model.add_constraint(hlist[0] == m)
    model.add_constraint(hlist[n] == h)

    # Starting from his age, the operations in the other order give my age.
    model.add_constraint(mlist[0] == h)
    model.add_constraint(mlist[n] == m)

    # Each step applies its operation: +2, /8 (as 8 * new == old, so only exact divisions),
    # -3, or *7.
    for order, vals in ((order1, hlist), (order2, mlist)):
        for i in steps:
            old, new = vals[i], vals[i + 1]
            model.add_indicator(order[i, 0], new == old + 2)
            model.add_indicator(order[i, 1], 8 * new == old)
            model.add_indicator(order[i, 2], new == old - 3)
            model.add_indicator(order[i, 3], new == 7 * old)

    return model, {"m": m, "h": h}


if __name__ == "__main__":
    model, outputs = create_model({})
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)

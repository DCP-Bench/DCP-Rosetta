# age_changing: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install mip numpy`) with:
#   python age_changing.py

import itertools

import mip

# The puzzle gives no age limit. Ages are taken as whole numbers from 0 to 150.
AGE_MAX = 150
# The largest value along a chain: 7 times (age + 2), since +2 may come before *7.
VAL_MAX = 7 * (AGE_MAX + 2)
# Large enough that a step does not restrict anything when its order is not the chosen one.
BIG_M = 8 * VAL_MAX + 3

# The four operations as (kind, number): +2, /8, -3 and *7.
OPS = [("add", 2), ("div", 8), ("sub", 3), ("mul", 7)]
# The 24 orders in which the four operations can be applied. An order lists indices into OPS.
ORDERS = list(itertools.permutations(range(len(OPS))))


def add_chain(model, start, end, prefix):
    # chosen[order] is 1 when the operations are applied in this order.
    chosen = {}
    for k, order in enumerate(ORDERS):
        b = model.add_var(name=f"{prefix}_order_{k}", var_type=mip.BINARY)
        chosen[order] = b

        # values[j] is the age after the first j operations of this order.
        values = [start]
        for i in range(len(OPS) - 1):
            values.append(model.add_var(name=f"{prefix}_{k}_v{i + 1}", lb=0, ub=VAL_MAX, var_type=mip.INTEGER))
        values.append(end)

        # Each operation links the age before it (now) to the age after it (after): +c, -c, *c, or /c, where /c needs now to be c times after.
        for step, op_index in enumerate(order):
            kind, c = OPS[op_index]
            now, after = values[step], values[step + 1]
            if kind == "add":
                lhs, rhs = after, now + c
            elif kind == "sub":
                lhs, rhs = after, now - c
            elif kind == "mul":
                lhs, rhs = after, c * now
            else:
                lhs, rhs = now, c * after
            model.add_constr(lhs - rhs <= BIG_M * (1 - b))
            model.add_constr(rhs - lhs <= BIG_M * (1 - b))

    # Exactly one order is applied.
    model.add_constr(mip.xsum(chosen.values()) == 1)
    return chosen


def create_model(instance):
    """Start with my age and apply the operations +2, /8, -3 and *7, each once and
    in some order: the result is my husband's age. Starting from his age and
    applying the same four operations in a different order gives my age. Find
    both ages."""
    model = mip.Model(solver_name="CBC")

    # My age and my husband's age, in whole years.
    m = model.add_var(name="m", lb=0, ub=AGE_MAX, var_type=mip.INTEGER)
    h = model.add_var(name="h", lb=0, ub=AGE_MAX, var_type=mip.INTEGER)

    # My age, taken through the operations in some order, gives his age.
    from_me = add_chain(model, m, h, "me_to_husband")
    # His age, taken through the operations in some order, gives mine.
    from_him = add_chain(model, h, m, "husband_to_me")

    # The two orders are different: no order is chosen for both.
    for order in ORDERS:
        model.add_constr(from_me[order] + from_him[order] <= 1)

    return model, {"h": h, "m": m}


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

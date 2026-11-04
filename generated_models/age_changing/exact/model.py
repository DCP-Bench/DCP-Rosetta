# age_changing: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install exact numpy`) with:
#   python age_changing.py

from itertools import permutations

from exact import Exact


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7, each once
    and in some order: the result is my husband's age. Starting from his age and
    applying the same four operations in a different order gives my age. What are
    our ages?"""
    n_ops = 4                    # the four operations: +2, /8, -3 and *7
    age_low, age_high = 16, 120  # adults are assumed to be 16 to 120 years old
    big = 8000                   # larger than any change an operation makes to a value from 1 to 1000

    solver = Exact()

    # Exact identifies its variables by name.
    # m is my age; h is my husband's age.
    solver.addVariable("m", age_low, age_high)
    solver.addVariable("h", age_low, age_high)

    # from_mine[i] is my age after the first i operations, and it ends at my husband's age.
    # from_his[i] is his age after the first i operations, and it ends at my age.
    # The puzzle does not give the ages along the way; they are taken as 1 to 1000.
    from_mine = ["m"] + [f"from_mine_{i}" for i in range(1, n_ops)] + ["h"]
    from_his = ["h"] + [f"from_his_{i}" for i in range(1, n_ops)] + ["m"]
    for i in range(1, n_ops):
        solver.addVariable(from_mine[i], 1, 1000)
        solver.addVariable(from_his[i], 1, 1000)

    # The operations are numbered 0 to 3 for +2, /8, -3 and *7. An order is one way to
    # arrange them; there are 4! = 24 orders. order_is[chain][k] is 1 when the chain uses order k.
    orders = list(permutations(range(n_ops)))
    order_is = {}
    for chain in ("perm1", "perm2"):
        order_is[chain] = [f"{chain}_order_{k}" for k in range(len(orders))]
        for name in order_is[chain]:
            solver.addVariable(name, 0, 1)

    # Adds the steps of one chain, which starts at the given ages and applies the operations
    # in the order the chain picks.
    def add_chain(chain, ages):
        for i in range(n_ops):
            for op in range(n_ops):
                # uses is 1 when step i applies operation op.
                uses = f"{chain}_step_{i}_uses_{op}"
                solver.addVariable(uses, 0, 1)
                # Step i applies op exactly when the chain's order puts op in position i.
                solver.addConstraint([(1, uses)] + [(-1, order_is[chain][k])
                                                    for k, order in enumerate(orders)
                                                    if order[i] == op], True, 0, True, 0)
                old, new = ages[i], ages[i + 1]
                left, right = {0: ([(1, new), (-1, old)], 2),  # new = old + 2
                               1: ([(8, new), (-1, old)], 0),  # 8 * new = old, old divided by 8
                               2: ([(1, new), (-1, old)], -3),  # new = old - 3
                               3: ([(1, new), (-7, old)], 0)}[op]  # new = old * 7
                # When step i applies op, the new age is the result of op on the old age.
                # Otherwise the two ages may differ by up to big.
                solver.addConstraint(left + [(big, uses)], False, 0, True, right + big)
                solver.addConstraint(left + [(-big, uses)], True, right - big)

    # Each chain uses exactly one order.
    for chain in ("perm1", "perm2"):
        solver.addConstraint([(1, name) for name in order_is[chain]], True, 1, True, 1)

    # The two chains never use the same order.
    for k in range(len(orders)):
        solver.addConstraint([(1, order_is["perm1"][k]), (1, order_is["perm2"][k])],
                             False, 0, True, 1)

    add_chain("perm1", from_mine)
    add_chain("perm2", from_his)

    return solver, {"m": "m", "h": "h"}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

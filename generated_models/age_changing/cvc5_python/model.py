# age_changing: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install cvc5 numpy`) with:
#   python age_changing.py

import cvc5.pythonic as c5


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7 in some
    order: the result is my husband's age. Starting with his age and applying the
    same four operations in a different order gives my age. What are our ages?"""

    def apply_steps(start, order, tag):
        # Apply the operations in the given order, one after the other. The codes are
        # 0 for +2, 1 for /8 (exact, so the value must be a multiple of 8), 2 for -3
        # and 3 for *7.
        steps = []
        value = start
        for k, op in enumerate(order):
            new_value = c5.Int(f"{tag}_{k}")
            steps += [
                c5.Implies(op == 0, new_value == value + 2),
                c5.Implies(op == 1, value == 8 * new_value),
                c5.Implies(op == 2, new_value == value - 3),
                c5.Implies(op == 3, new_value == 7 * value),
            ]
            value = new_value
        return steps, value

    # My age and my husband's age.
    m, h = c5.Ints("m h")
    # mine_order[k] is the operation applied k-th, starting from my age.
    mine_order = [c5.Int(f"mine_order_{k}") for k in range(4)]
    # his_order[k] is the operation applied k-th, starting from his age.
    his_order = [c5.Int(f"his_order_{k}") for k in range(4)]

    solver = c5.Solver()

    # The ages are not negative.
    solver.add(m >= 0, h >= 0)
    # Each operation code is 0 to 3.
    solver.add([c5.And(op >= 0, op <= 3) for op in mine_order + his_order])
    # Each order uses every operation once.
    solver.add(c5.Distinct(mine_order), c5.Distinct(his_order))
    # The two orders differ in at least one step.
    solver.add(c5.Or(*[x != y for x, y in zip(mine_order, his_order)]))
    # Starting from my age, the operations in my order give his age.
    steps_mine, end_mine = apply_steps(m, mine_order, "a")
    solver.add(c5.And(*steps_mine, end_mine == h))
    # Starting from his age, the operations in his order give my age.
    steps_his, end_his = apply_steps(h, his_order, "b")
    solver.add(c5.And(*steps_his, end_his == m))

    return solver, {"h": h, "m": m}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

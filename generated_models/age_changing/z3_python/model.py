# age_changing: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install z3-solver numpy`) with:
#   python age_changing.py

import z3


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7 in some
    order: the result is my husband's age. Starting with his age and applying the
    same four operations in a different order gives my age. What are our ages?"""
    # The puzzle states its own operations, so the instance holds no data.
    # The ages are not given: we assume adult ages between 16 and 120.
    age_low, age_high = 16, 120
    # The number of operations.
    n_ops = 4

    # My age and my husband's age.
    m = z3.Int("m")
    h = z3.Int("h")

    # perm1[i] is the operation applied i-th when starting from my age, and perm2[i]
    # the operation applied i-th when starting from his age.
    # Operations: 0 is +2, 1 is /8, 2 is -3, 3 is *7.
    perm1 = [z3.Int(f"perm1_{i}") for i in range(n_ops)]
    perm2 = [z3.Int(f"perm2_{i}") for i in range(n_ops)]
    # from_mine[i] is my age after the first i operations, and from_his[i] is the same
    # starting from his age. The puzzle does not bound these intermediate ages, so they
    # are taken as whole numbers from 1 to 1000.
    from_mine = [z3.Int(f"from_mine_{i}") for i in range(n_ops + 1)]
    from_his = [z3.Int(f"from_his_{i}") for i in range(n_ops + 1)]

    def apply(op, old, new):
        """The operation numbered op turns the age old into the age new."""
        # Division by 8 is written as multiplication: 8 times the result is the old age.
        return z3.And(
            z3.Implies(op == 0, new == old + 2),
            z3.Implies(op == 1, 8 * new == old),
            z3.Implies(op == 2, new == old - 3),
            z3.Implies(op == 3, new == old * 7),
        )

    solver = z3.Solver()

    # Both ages are between 16 and 120.
    solver.add(z3.And(age_low <= m, m <= age_high),
               z3.And(age_low <= h, h <= age_high))

    # Each operation number is one of the four operations.
    solver.add([z3.And(0 <= p, p < n_ops) for p in perm1 + perm2])

    # The intermediate ages are whole numbers from 1 to 1000.
    solver.add([z3.And(1 <= v, v <= 1000) for v in from_mine + from_his])

    # Each order uses every operation once.
    solver.add(z3.Distinct(perm1), z3.Distinct(perm2))

    # The two orders differ in at least one step.
    solver.add(z3.Or([p1 != p2 for p1, p2 in zip(perm1, perm2)]))

    # Starting from my age and applying the operations gives his age.
    solver.add(from_mine[0] == m, h == from_mine[n_ops])

    # Starting from his age and applying the operations gives my age.
    solver.add(from_his[0] == h, m == from_his[n_ops])

    # Each step applies the operation chosen for it in its order.
    for i in range(n_ops):
        solver.add(apply(perm1[i], from_mine[i], from_mine[i + 1]))
        solver.add(apply(perm2[i], from_his[i], from_his[i + 1]))

    return solver, {"m": m, "h": h}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

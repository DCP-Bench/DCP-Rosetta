# age_changing: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install cpmpy`) with:
#   python age_changing.py

import cpmpy as cp


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7 in some
    order: the result is my husband's age. Starting with his age and applying the
    same four operations in a different order gives my age. What are our ages?"""
    # The puzzle states its own operations, so the instance holds no data.
    # The ages are not given: we assume adult ages between 16 and 120.
    n = 4                      # number of operations
    age_low, age_high = 16, 120

    # m is my age, h is my husband's age
    m = cp.intvar(age_low, age_high, name="m")
    h = cp.intvar(age_low, age_high, name="h")

    # perm1[i] is the operation applied i-th when starting from my age,
    # perm2[i] the one applied i-th when starting from his age.
    # Operations: 0 is +2, 1 is /8, 2 is -3, 3 is *7.
    perm1 = cp.intvar(0, n - 1, shape=n, name="perm1")
    perm2 = cp.intvar(0, n - 1, shape=n, name="perm2")

    # Every value along the way is assumed to be a whole number between 1 and 1000;
    # the puzzle does not bound it.
    # hlist[i] is the value after i operations starting from my age;
    # mlist[i] is the same starting from his age.
    hlist = cp.intvar(1, 1000, shape=n + 1, name="hlist")
    mlist = cp.intvar(1, 1000, shape=n + 1, name="mlist")

    def apply(op, old, new):
        # new is the result of applying operation op to old.
        # The division is written as 8 * new == old, so it only holds when exact.
        return [
            (op == 0).implies(new == old + 2),
            (op == 1).implies(new * 8 == old),
            (op == 2).implies(new == old - 3),
            (op == 3).implies(new == old * 7),
        ]

    model = cp.Model()
    # Each ordering uses every operation exactly once.
    model.add(cp.AllDifferent(perm1))
    model.add(cp.AllDifferent(perm2))
    # The two orderings are different.
    model.add(cp.sum(perm1 != perm2) > 0)
    # Starting from my age and applying the operations gives his age.
    model.add(hlist[0] == m)
    model.add(hlist[n] == h)
    # Starting from his age and applying the operations gives my age.
    model.add(mlist[0] == h)
    model.add(mlist[n] == m)
    # Each step of both sequences applies the operation chosen for it.
    for i in range(n):
        model.add(apply(perm1[i], hlist[i], hlist[i + 1]))
        model.add(apply(perm2[i], mlist[i], mlist[i + 1]))

    return model, {"m": m, "h": h}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

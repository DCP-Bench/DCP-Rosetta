# age_changing: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install pychoco numpy`) with:
#   python age_changing.py

from pychoco.model import Model


def apply(op, old):
    """The value after applying operation op to old, or None when the division by 8
    does not give a whole number. Operations are numbered 0 for +2, 1 for /8, 2 for -3
    and 3 for *7."""
    if op == 0:
        return old + 2
    if op == 1:
        return old // 8 if old % 8 == 0 else None
    if op == 2:
        return old - 3
    return old * 7


def create_model(instance):
    """Start with my age and apply the operations +2, /8, -3 and *7, each once and in
    some order: the result is my husband's age. Starting from his age and applying the
    same four operations in a different order gives my age. Find both ages."""
    model = Model()

    # The four operations.
    n_ops = 4
    # Adult ages are whole years from 16 to 120.
    age_low, age_high = 16, 120
    # Values along the way are whole numbers from 1 to 1000.
    value_low, value_high = 1, 1000

    # My age.
    m = model.intvar(age_low, age_high, name="m")
    # My husband's age.
    h = model.intvar(age_low, age_high, name="h")

    # perm1[i] is the operation at step i going from my age to his, and perm2[i] the
    # operation at step i going from his age to mine.
    perm1 = [model.intvar(0, n_ops - 1, name=f"perm1_{i}") for i in range(n_ops)]
    perm2 = [model.intvar(0, n_ops - 1, name=f"perm2_{i}") for i in range(n_ops)]
    # hlist[i] is the value after i steps from my age, and mlist[i] the value after i
    # steps from his age.
    hlist = [model.intvar(value_low, value_high, name=f"hlist_{i}") for i in range(n_ops + 1)]
    mlist = [model.intvar(value_low, value_high, name=f"mlist_{i}") for i in range(n_ops + 1)]

    # Each order uses all four operations, once each.
    model.all_different(perm1).post()
    model.all_different(perm2).post()

    # differs[i] is true when the two orders use different operations at step i.
    differs = [model.arithm(perm1[i], "!=", perm2[i]).reify() for i in range(n_ops)]
    # The two orders differ at some step.
    model.sum(differs, ">=", 1).post()

    # The chain from my age ends at my husband's age.
    model.arithm(hlist[0], "=", m).post()
    model.arithm(hlist[n_ops], "=", h).post()
    # The chain from his age ends at my age.
    model.arithm(mlist[0], "=", h).post()
    model.arithm(mlist[n_ops], "=", m).post()

    # The steps allowed: an operation applied to a value, with a result in range.
    steps = []
    for op in range(n_ops):
        for old in range(value_low, value_high + 1):
            new = apply(op, old)
            if new is not None and value_low <= new <= value_high:
                steps.append((op, old, new))
    # Each step of each chain is one of the allowed steps.
    for i in range(n_ops):
        model.table([perm1[i], hlist[i], hlist[i + 1]], steps).post()
        model.table([perm2[i], mlist[i], mlist[i + 1]], steps).post()

    return model, {"m": m, "h": h}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

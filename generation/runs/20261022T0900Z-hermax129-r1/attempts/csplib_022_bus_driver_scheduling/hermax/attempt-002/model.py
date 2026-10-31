from hermax.model import Model


def build(instance):
    # Bus driver scheduling (set partitioning): choose shifts so every task is covered
    # exactly once, minimising the number of chosen shifts.
    num_work = instance["num_work"]
    shifts = [list(s) for s in instance["shifts"]]
    num_shifts = len(shifts)

    m = Model()

    x = m.bool_vector("x", num_shifts)

    # For each task, the chosen shifts that cover it must number exactly one.
    for w in range(num_work):
        covering = [x[s] for s in range(num_shifts) if w in shifts[s]]
        m &= (sum(covering) == 1)

    # Minimise the number of selected shifts (every shift has the same cost).
    m.obj += sum(x)

    return m, {"x": x}

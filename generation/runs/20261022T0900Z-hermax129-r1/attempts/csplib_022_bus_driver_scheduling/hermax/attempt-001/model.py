from hermax.model import Model


def build(instance):
    # Read instance
    num_shifts = instance["num_shifts"]
    num_work = instance["num_work"]
    shifts = instance["shifts"]  # shifts[i] is list of tasks covered by shift i

    m = Model()

    # Decision: which shifts to select
    x = m.bool_vector("x", num_shifts)

    # Constraint: each task must be covered by exactly one shift
    for task in range(num_work):
        # Find which shifts cover this task
        shifts_covering_task = [i for i in range(num_shifts) if task in shifts[i]]
        # Exactly one must be selected
        if shifts_covering_task:
            m &= (sum(x[i] for i in shifts_covering_task) == 1)

    # Objective: minimize number of shifts used
    # Soft clauses: pay when x[i] is true (selected)
    for i in range(num_shifts):
        m.obj[1] += x[i]

    return m, {"x": x}

# age_changing: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Run it (after `pip install ortools`) with:
#   python age_changing.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7 in some
    order: the result is my husband's age. Starting with his age and applying the
    same four operations in a different order gives my age. What are our ages?"""
    model = cp_model.CpModel()

    # The ages are not given: we assume adult ages between 16 and 120.
    age_low, age_high = 16, 120
    # The number of operations.
    n_ops = 4

    # My age.
    m = model.new_int_var(age_low, age_high, "m")
    # My husband's age.
    h = model.new_int_var(age_low, age_high, "h")

    # perm1[i] is the operation applied i-th when starting from my age, and perm2[i]
    # the operation applied i-th when starting from his age.
    # Operations: 0 is +2, 1 is /8, 2 is -3, 3 is *7.
    perm1 = [model.new_int_var(0, n_ops - 1, f"perm1_{i}") for i in range(n_ops)]
    perm2 = [model.new_int_var(0, n_ops - 1, f"perm2_{i}") for i in range(n_ops)]
    # from_mine[i] is my age after the first i operations. from_his[i] is the same,
    # starting from his age. The puzzle does not bound these intermediate ages, so
    # they are taken as whole numbers from 1 to 1000.
    from_mine = [model.new_int_var(1, 1000, f"from_mine_{i}") for i in range(n_ops + 1)]
    from_his = [model.new_int_var(1, 1000, f"from_his_{i}") for i in range(n_ops + 1)]

    def apply(op, old, new):
        # results[code] holds when new is old after operation code. Dividing by 8
        # needs old to be divisible by 8.
        results = [new == old + 2, 8 * new == old, new == old - 3, new == old * 7]
        for code, result in enumerate(results):
            # chosen is true exactly when op is operation code.
            chosen = model.new_bool_var(f"chosen_{code}")
            model.add(op == code).only_enforce_if(chosen)
            model.add(op != code).only_enforce_if(~chosen)
            model.add(result).only_enforce_if(chosen)

    # Each order uses every operation exactly once.
    model.add_all_different(perm1)
    model.add_all_different(perm2)

    # differs[i] is true when the two orders use different operations at step i.
    differs = []
    for i in range(n_ops):
        bit = model.new_bool_var(f"differs_{i}")
        model.add(perm1[i] != perm2[i]).only_enforce_if(bit)
        model.add(perm1[i] == perm2[i]).only_enforce_if(~bit)
        differs.append(bit)
    # The two orders differ in at least one place.
    model.add_bool_or(differs)

    # Starting from my age and applying the operations gives his age.
    model.add(from_mine[0] == m)
    model.add(h == from_mine[n_ops])
    # Starting from his age and applying the operations gives my age.
    model.add(from_his[0] == h)
    model.add(m == from_his[n_ops])

    # Each step applies the operation chosen for it in its order.
    for i in range(n_ops):
        apply(perm1[i], from_mine[i], from_mine[i + 1])
        apply(perm2[i], from_his[i], from_his[i + 1])

    return model, {"m": m, "h": h}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

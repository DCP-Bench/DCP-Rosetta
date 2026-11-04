# allergy: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install ortools`) with:
#   python allergy.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Four friends are each allergic to something different (eggs, mold, nuts,
    ragweed) and each has a different surname (Baxter, Lemon, Malone, Fleet).
    Match each allergy and each surname to a friend, given the clues."""
    # The friends: Debra is 0, Janet 1, Hugh 2, Rick 3.
    debra, janet, hugh, rick = range(4)

    model = cp_model.CpModel()
    # foods[k] is the friend allergic to food k
    foods = [model.new_int_var(0, 3, f"food_{k}") for k in range(4)]
    eggs, mold, nuts, ragweed = foods
    # surnames[k] is the friend with surname k
    surnames = [model.new_int_var(0, 3, f"surname_{k}") for k in range(4)]
    baxter, lemon, malone, fleet = surnames

    # Each friend has a different allergy and a different surname.
    model.add_all_different(foods)
    model.add_all_different(surnames)

    # Rick is not allergic to mold.
    model.add(mold != rick)
    # Baxter is allergic to eggs.
    model.add(eggs == baxter)
    # Hugh is neither surnamed Lemon nor Fleet.
    model.add(lemon != hugh)
    model.add(fleet != hugh)
    # Debra is allergic to ragweed.
    model.add(ragweed == debra)
    # Janet is not surnamed Lemon, and is allergic to neither eggs nor mold.
    model.add(lemon != janet)
    model.add(eggs != janet)
    model.add(mold != janet)

    return model, {
        "eggs": eggs,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
        "baxter": baxter,
        "lemon": lemon,
        "malone": malone,
        "fleet": fleet,
    }


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

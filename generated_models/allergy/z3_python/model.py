# allergy: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install z3-solver numpy`) with:
#   python allergy.py

import z3


def create_model(instance):
    """Four friends, two women (Debra and Janet) and two men (Hugh and Rick), each have
    a different allergy (eggs, mold, nuts or ragweed) and a different surname (Baxter,
    Lemon, Malone or Fleet). Match each allergy and each surname to a friend."""
    n_friends = 4
    # The friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    debra, janet, hugh, rick = range(n_friends)

    # foods[k] is the friend allergic to the k-th food, in the order eggs, mold, nuts, ragweed.
    eggs, mold, nuts, ragweed = foods = z3.Ints("eggs mold nuts ragweed")
    # surnames[k] is the friend with the k-th surname, in the order Baxter, Lemon, Malone, Fleet.
    baxter, lemon, malone, fleet = surnames = z3.Ints("baxter lemon malone fleet")

    solver = z3.Solver()

    # Each food and each surname belongs to one of the friends.
    solver.add([z3.And(0 <= v, v < n_friends) for v in foods + surnames])

    # Each friend has a different allergy and a different surname.
    solver.add(z3.Distinct(foods), z3.Distinct(surnames))

    # Rick is not allergic to mold.
    solver.add(mold != rick)
    # Baxter is allergic to eggs.
    solver.add(eggs == baxter)
    # Hugh is neither Lemon nor Fleet.
    solver.add(lemon != hugh, fleet != hugh)
    # Debra is allergic to ragweed.
    solver.add(ragweed == debra)
    # Janet is not Lemon, and is allergic to neither eggs nor mold.
    solver.add(lemon != janet, eggs != janet, mold != janet)

    return solver, {
        "eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
        "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet,
    }


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

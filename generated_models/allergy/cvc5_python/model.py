# allergy: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install cvc5 numpy`) with:
#   python allergy.py

import cvc5.pythonic as c5


def create_model(instance):
    """Four friends are each allergic to something different (eggs, mold, nuts,
    ragweed) and each has a different surname (Baxter, Lemon, Malone, Fleet).
    Match each allergy and each surname to a friend, given the clues."""
    # The friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3.
    debra, janet, hugh, rick = 0, 1, 2, 3

    # baxter, lemon, malone and fleet are the friends with those surnames.
    baxter, lemon, malone, fleet = c5.Ints("baxter lemon malone fleet")
    surnames = [baxter, lemon, malone, fleet]

    # eggs, mold, nuts and ragweed are the friends with those allergies.
    eggs, mold, nuts, ragweed = c5.Ints("eggs mold nuts ragweed")
    allergies = [eggs, mold, nuts, ragweed]

    solver = c5.Solver()

    # Each name is the number of one of the four friends.
    for v in surnames + allergies:
        solver.add(v >= 0, v <= 3)

    # Each friend has a different surname, and a different allergy.
    solver.add(c5.Distinct(surnames))
    solver.add(c5.Distinct(allergies))

    # Rick is not allergic to mold.
    solver.add(mold != rick)

    # Baxter is allergic to eggs.
    solver.add(baxter == eggs)

    # Hugh is neither surnamed Lemon nor Fleet.
    solver.add(lemon != hugh, fleet != hugh)

    # Debra is allergic to ragweed.
    solver.add(ragweed == debra)

    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    solver.add(lemon != janet, eggs != janet, mold != janet)

    outputs = {
        "baxter": baxter,
        "eggs": eggs,
        "fleet": fleet,
        "lemon": lemon,
        "malone": malone,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
    }
    return solver, outputs


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

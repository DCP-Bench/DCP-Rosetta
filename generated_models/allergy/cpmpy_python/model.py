# allergy: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install cpmpy`) with:
#   python allergy.py

import cpmpy as cp


def create_model(instance):
    """Four friends are each allergic to something different (eggs, mold, nuts,
    ragweed) and have a different surname (Baxter, Lemon, Malone, Fleet). Match
    each allergy and each surname to a friend, given the clues. The puzzle fixes
    its own data, so instance is not used."""
    # Friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3
    debra, janet, hugh, rick = range(4)

    # foods[k] is the friend allergic to food k (eggs, mold, nuts, ragweed)
    foods = cp.intvar(0, 3, shape=4, name="foods")
    eggs, mold, nuts, ragweed = foods
    # surnames[k] is the friend with surname k (Baxter, Lemon, Malone, Fleet)
    surnames = cp.intvar(0, 3, shape=4, name="surnames")
    baxter, lemon, malone, fleet = surnames

    model = cp.Model()

    # Each friend has a different allergy and a different surname.
    model.add(cp.AllDifferent(foods))
    model.add(cp.AllDifferent(surnames))

    # Rick is not allergic to mold.
    model.add(mold != rick)
    # Baxter is allergic to eggs.
    model.add(eggs == baxter)
    # Hugh is neither surnamed Lemon nor Fleet.
    model.add(lemon != hugh)
    model.add(fleet != hugh)
    # Debra is allergic to ragweed.
    model.add(ragweed == debra)
    # Janet is not Lemon, and is allergic to neither eggs nor mold.
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
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

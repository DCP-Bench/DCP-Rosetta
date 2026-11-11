# allergy: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python allergy.py

from pycsp3 import *


def create_model(instance):
    """Four friends, two women (Debra and Janet) and two men (Hugh and Rick), are each
    allergic to something different: eggs, mold, nuts or ragweed. Each has a different
    surname: Baxter, Lemon, Malone or Fleet. Match each friend's surname with his or her
    allergy, given the clues."""
    # The friends are numbered: Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    n_friends = 4
    debra, janet, hugh, rick = 0, 1, 2, 3

    # Each food is the allergy of exactly one friend: the friend's number.
    eggs = Var(dom=range(n_friends))     # the friend allergic to eggs
    mold = Var(dom=range(n_friends))     # the friend allergic to mold
    nuts = Var(dom=range(n_friends))     # the friend allergic to nuts
    ragweed = Var(dom=range(n_friends))  # the friend allergic to ragweed

    # Each surname belongs to exactly one friend: the friend's number.
    baxter = Var(dom=range(n_friends))   # the friend surnamed Baxter
    lemon = Var(dom=range(n_friends))    # the friend surnamed Lemon
    malone = Var(dom=range(n_friends))   # the friend surnamed Malone
    fleet = Var(dom=range(n_friends))    # the friend surnamed Fleet

    satisfy(
        # Each friend has a different allergy.
        AllDifferent(eggs, mold, nuts, ragweed),
        # Each friend has a different surname.
        AllDifferent(baxter, lemon, malone, fleet),
        # Rick is not allergic to mold.
        mold != rick,
        # Baxter is allergic to eggs.
        eggs == baxter,
        # Debra is allergic to ragweed.
        ragweed == debra,
        # Hugh is neither surnamed Lemon nor Fleet.
        lemon != hugh,
        fleet != hugh,
        # Janet, who is not Lemon, is neither allergic to eggs nor to mold.
        lemon != janet,
        eggs != janet,
        mold != janet,
    )

    return {
        "baxter": baxter,
        "eggs": eggs,
        "fleet": fleet,
        "lemon": lemon,
        "malone": malone,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

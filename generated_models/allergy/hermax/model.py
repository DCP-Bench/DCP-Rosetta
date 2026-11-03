# allergy: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install hermax`) with:
#   python allergy.py
from hermax.model import Model


def create_model(instance):
    """Four friends, Debra, Janet, Hugh and Rick, are each allergic to something different
    (eggs, mold, nuts or ragweed), and each has a different surname (Baxter, Lemon, Malone
    or Fleet). From the clues, match every allergy and every surname with its friend.

    The instance is not read: the statement fixes all the data, so the friends and clues
    are written here as constants."""
    # The four friends, numbered as in the statement.
    Debra, Janet, Hugh, Rick = 0, 1, 2, 3
    n = 4

    m = Model()
    # allergen[k] is the friend allergic to the k-th allergen (0 eggs, 1 mold, 2 nuts, 3 ragweed)
    allergen = m.int_vector("allergen", n, 0, n - 1)
    eggs, mold, nuts, ragweed = allergen[0], allergen[1], allergen[2], allergen[3]
    # surname[k] is the friend with the k-th surname (0 Baxter, 1 Lemon, 2 Malone, 3 Fleet)
    surname = m.int_vector("surname", n, 0, n - 1)
    baxter, lemon, malone, fleet = surname[0], surname[1], surname[2], surname[3]

    # Each friend is allergic to a different thing, and has a different surname.
    m &= allergen.all_different()
    m &= surname.all_different()

    # Rick is not allergic to mold.
    m &= (mold != Rick)
    # Baxter is allergic to eggs: the friend allergic to eggs is the one surnamed Baxter.
    m &= (eggs == baxter)
    # Hugh is neither surnamed Lemon nor Fleet.
    m &= (lemon != Hugh)
    m &= (fleet != Hugh)
    # Debra is allergic to ragweed.
    m &= (ragweed == Debra)
    # Janet is not surnamed Lemon, and is allergic neither to eggs nor to mold.
    m &= (lemon != Janet)
    m &= (eggs != Janet)
    m &= (mold != Janet)

    # No objective: any assignment satisfying the clues is an answer.
    return m, {"eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
               "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

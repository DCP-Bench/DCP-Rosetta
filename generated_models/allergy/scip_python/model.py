# allergy: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python allergy.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Four friends, Debra, Janet, Hugh and Rick, each have a different allergy
    (eggs, mold, nuts or ragweed) and a different surname (Baxter, Lemon, Malone
    or Fleet). Match each friend's surname and allergy so that every clue in the
    statement holds.

    The instance file is empty ([]): the statement fixes all the data, so nothing
    is read from the instance argument.
    """
    model = Model("allergy")

    # The friends, in the statement's numbering: Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    DEBRA, JANET, HUGH, RICK = range(4)
    # The allergies, in the order the statement lists them.
    EGGS, MOLD, NUTS, RAGWEED = range(4)
    # The surnames, in the order the statement lists them.
    BAXTER, LEMON, MALONE, FLEET = range(4)

    # allergy[f, a] is 1 when friend f is allergic to allergy a, and 0 otherwise.
    # Each friend has exactly one allergy, and the statement says each is allergic to
    # something different, so with four friends and four allergies the 4x4 grid is a
    # permutation matrix (one 1 in every row and column).
    allergy = model.addMatrixVar((4, 4), vtype="B", name="allergy")
    model.addMatrixCons(allergy.sum(axis=1) == 1)  # each friend has exactly one allergy
    model.addMatrixCons(allergy.sum(axis=0) == 1)  # each allergy belongs to exactly one friend

    # surname[f, s] is 1 when friend f has surname s, and 0 otherwise.
    # The same permutation structure: one surname per friend, one friend per surname.
    surname = model.addMatrixVar((4, 4), vtype="B", name="surname")
    model.addMatrixCons(surname.sum(axis=1) == 1)  # each friend has exactly one surname
    model.addMatrixCons(surname.sum(axis=0) == 1)  # each surname belongs to exactly one friend

    # Rick is not allergic to mold.
    model.addCons(allergy[RICK, MOLD] == 0)

    # Baxter is allergic to eggs: the friend surnamed Baxter is the friend allergic to eggs.
    # For every friend f: f is surnamed Baxter exactly when f is allergic to eggs
    # (column BAXTER of surname equals column EGGS of allergy).
    model.addMatrixCons(surname[:, BAXTER] == allergy[:, EGGS])

    # Hugh is neither surnamed Lemon nor surnamed Fleet.
    model.addCons(surname[HUGH, LEMON] == 0)
    model.addCons(surname[HUGH, FLEET] == 0)

    # Debra is allergic to ragweed.
    model.addCons(allergy[DEBRA, RAGWEED] == 1)

    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    model.addCons(surname[JANET, LEMON] == 0)
    model.addCons(allergy[JANET, EGGS] == 0)
    model.addCons(allergy[JANET, MOLD] == 0)

    # Each output is the number of the friend (0 to 3) who has that allergy or that
    # surname. The sum is over the one-hot grid, so it picks out exactly one friend.
    outputs = {
        "eggs": quicksum(f * allergy[f, EGGS] for f in range(4)),
        "mold": quicksum(f * allergy[f, MOLD] for f in range(4)),
        "nuts": quicksum(f * allergy[f, NUTS] for f in range(4)),
        "ragweed": quicksum(f * allergy[f, RAGWEED] for f in range(4)),
        "baxter": quicksum(f * surname[f, BAXTER] for f in range(4)),
        "lemon": quicksum(f * surname[f, LEMON] for f in range(4)),
        "malone": quicksum(f * surname[f, MALONE] for f in range(4)),
        "fleet": quicksum(f * surname[f, FLEET] for f in range(4)),
    }

    # The statement asks for a matching only, so there is no objective.
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

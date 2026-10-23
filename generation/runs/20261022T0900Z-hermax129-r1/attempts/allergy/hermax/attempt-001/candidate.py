from hermax.model import Model


def build(instance):
    """
    Logic puzzle: match 4 friends with their allergies and surnames.
    - People: Debra (0), Janet (1), Hugh (2), Rick (3)
    - Allergies: eggs, mold, nuts, ragweed
    - Surnames: Baxter, Lemon, Malone, Fleet

    Outputs are: which person has each allergy/surname.
    Each output is in range 0-3.
    """

    m = Model()

    # Each allergy and surname is assigned to exactly one person (0-3)
    allergies = m.int_vector("allergy", 4, 0, 3)
    eggs, mold, nuts, ragweed = allergies

    surnames = m.int_vector("surname", 4, 0, 3)
    baxter, lemon, malone, fleet = surnames

    # All allergies are different (each person gets exactly one allergy)
    m &= allergies.all_different()

    # All surnames are different (each person gets exactly one surname)
    m &= surnames.all_different()

    # Fixed constraints from the problem description
    # Rick (3) is not allergic to mold
    m &= (mold != 3)

    # Baxter is allergic to eggs
    m &= (baxter == eggs)

    # Hugh (2) is neither surnamed Lemon nor Fleet
    m &= (lemon != 2)
    m &= (fleet != 2)

    # Debra (0) is allergic to ragweed
    m &= (ragweed == 0)

    # Janet (1) isn't Lemon and is neither allergic to eggs nor to mold
    m &= (lemon != 1)
    m &= (eggs != 1)
    m &= (mold != 1)

    return m, {
        "eggs": eggs,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
        "baxter": baxter,
        "lemon": lemon,
        "malone": malone,
        "fleet": fleet,
    }

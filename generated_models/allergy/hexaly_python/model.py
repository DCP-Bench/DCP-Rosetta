"""Allergy: match four friends (Debra 0, Janet 1, Hugh 2, Rick 3) with an allergy and a surname each."""
import hexaly.optimizer as hx

DEBRA, JANET, HUGH, RICK = range(4)


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each allergy and each surname belongs to one friend, the friend's number
    allergies = {name: model.int(0, 3) for name in ("eggs", "mold", "nuts", "ragweed")}
    surnames = {name: model.int(0, 3) for name in ("baxter", "lemon", "malone", "fleet")}  # the friend (0 to 3) who has each surname
    # Each friend has a different allergy and a different surname
    for group in (list(allergies.values()), list(surnames.values())):
        for a in range(4):
            for b in range(a + 1, 4):
                model.constraint(group[a] != group[b])

    # Rick is not allergic to mold
    model.constraint(allergies["mold"] != RICK)
    # Baxter is allergic to eggs
    model.constraint(surnames["baxter"] == allergies["eggs"])
    # Hugh is neither surnamed Lemon nor Fleet
    model.constraint(surnames["lemon"] != HUGH)
    model.constraint(surnames["fleet"] != HUGH)
    # Debra is allergic to ragweed
    model.constraint(allergies["ragweed"] == DEBRA)
    # Janet is not Lemon and is allergic to neither eggs nor mold
    model.constraint(surnames["lemon"] != JANET)
    model.constraint(allergies["eggs"] != JANET)
    model.constraint(allergies["mold"] != JANET)

    return optimizer, {**allergies, **surnames}

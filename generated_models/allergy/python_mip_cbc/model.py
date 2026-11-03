# allergy: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install mip numpy`) with:
#   python allergy.py

import mip


def create_model(instance):
    """Four friends are each allergic to something different (eggs, mold, nuts,
    ragweed) and each has a different surname (Baxter, Lemon, Malone, Fleet).
    Match each allergy and each surname to a friend, given the clues."""
    # The friends, numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    friends = range(4)
    debra, janet, hugh, rick = friends
    # The four allergies and the four surnames.
    allergies = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    model = mip.Model(solver_name="CBC")

    # allergic[f, k] is 1 when friend f is allergic to k, and 0 when not.
    allergic = {
        (f, k): model.add_var(f"allergic_{f}_{k}", var_type=mip.BINARY)
        for f in friends for k in allergies
    }
    # surnamed[f, s] is 1 when friend f has surname s, and 0 when not.
    surnamed = {
        (f, s): model.add_var(f"surnamed_{f}_{s}", var_type=mip.BINARY)
        for f in friends for s in surnames
    }

    # Each friend has exactly one allergy and exactly one surname.
    for f in friends:
        model += mip.xsum(allergic[f, k] for k in allergies) == 1
        model += mip.xsum(surnamed[f, s] for s in surnames) == 1

    # Each allergy and each surname belongs to exactly one friend.
    for k in allergies:
        model += mip.xsum(allergic[f, k] for f in friends) == 1
    for s in surnames:
        model += mip.xsum(surnamed[f, s] for f in friends) == 1

    # holder[name] is the friend who has that allergy or surname, as a number from 0 to 3.
    holder = {}
    for k in allergies:
        holder[k] = model.add_var(f"holder_{k}", lb=0, ub=3, var_type=mip.INTEGER)
        model += holder[k] == mip.xsum(f * allergic[f, k] for f in friends)
    for s in surnames:
        holder[s] = model.add_var(f"holder_{s}", lb=0, ub=3, var_type=mip.INTEGER)
        model += holder[s] == mip.xsum(f * surnamed[f, s] for f in friends)

    # Rick is not allergic to mold.
    allergic[rick, "mold"].ub = 0
    # Baxter is allergic to eggs.
    model += holder["baxter"] == holder["eggs"]
    # Hugh is neither surnamed Lemon nor Fleet.
    surnamed[hugh, "lemon"].ub = 0
    surnamed[hugh, "fleet"].ub = 0
    # Debra is allergic to ragweed.
    allergic[debra, "ragweed"].lb = 1
    # Janet is not surnamed Lemon.
    surnamed[janet, "lemon"].ub = 0
    # Janet is allergic to neither eggs nor mold.
    allergic[janet, "eggs"].ub = 0
    allergic[janet, "mold"].ub = 0

    return model, holder


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

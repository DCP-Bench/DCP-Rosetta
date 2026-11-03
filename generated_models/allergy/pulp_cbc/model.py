# allergy: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install pulp numpy`) with:
#   python allergy.py

import pulp


def create_model(instance):
    """Four friends (Debra, Janet, Hugh and Rick) are each allergic to a different one
    of eggs, mold, nuts and ragweed, and each has a different surname (Baxter, Lemon,
    Malone and Fleet). Match the allergies and the surnames to the friends using the
    clues."""
    # Debra, Janet, Hugh and Rick are friends 0, 1, 2 and 3.
    friends = Debra, Janet, Hugh, Rick = list(range(4))
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    problem = pulp.LpProblem("allergy", pulp.LpMinimize)

    # food[f][p] is 1 when friend p is allergic to food f.
    food = {f: [pulp.LpVariable(f"food_{f}_{p}", cat="Binary") for p in friends] for f in foods}
    # surname[s][p] is 1 when friend p has surname s.
    surname = {s: [pulp.LpVariable(f"surname_{s}_{p}", cat="Binary") for p in friends]
               for s in surnames}

    for matching, keys in ((food, foods), (surname, surnames)):
        # Each allergy (surname) belongs to exactly one friend.
        for key in keys:
            problem += pulp.lpSum(matching[key]) == 1
        # Each friend has exactly one allergy (surname), so no two share one.
        for p in friends:
            problem += pulp.lpSum(matching[key][p] for key in keys) == 1

    # Rick is not allergic to mold.
    problem += food["mold"][Rick] == 0
    # Baxter is allergic to eggs.
    for p in friends:
        problem += food["eggs"][p] == surname["baxter"][p]
    # Hugh is neither surnamed Lemon nor Fleet.
    problem += surname["lemon"][Hugh] == 0
    problem += surname["fleet"][Hugh] == 0
    # Debra is allergic to ragweed.
    problem += food["ragweed"][Debra] == 1
    # Janet is not surnamed Lemon, and is allergic to neither eggs nor mold.
    problem += surname["lemon"][Janet] == 0
    problem += food["eggs"][Janet] == 0
    problem += food["mold"][Janet] == 0

    # Each allergy and each surname, as the number of the friend it belongs to.
    outputs = {f: pulp.lpSum(p * food[f][p] for p in friends) for f in foods}
    outputs.update({s: pulp.lpSum(p * surname[s][p] for p in friends) for s in surnames})
    return problem, outputs


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

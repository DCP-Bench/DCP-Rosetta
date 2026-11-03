# allergy: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/allergy.html
# Run it (after `pip install exact numpy`) with:
#   python allergy.py

from exact import Exact


def create_model(instance):
    """Four friends each have a different allergy (eggs, mold, nuts, ragweed) and a
    different surname (Baxter, Lemon, Malone, Fleet). Match each allergy and each
    surname to a friend, using the clues."""
    # The friends are numbered Debra = 0, Janet = 1, Hugh = 2, Rick = 3.
    n = 4
    debra, janet, hugh, rick = range(n)

    # The allergies and the surnames. Each name stands for the friend who has it.
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]
    names = foods + surnames

    # Each (name, friend) pair is a clue that this friend does not have this name.
    ruled_out = {
        ("mold", rick),    # Rick is not allergic to mold
        ("lemon", hugh),   # Hugh is not surnamed Lemon
        ("fleet", hugh),   # Hugh is not surnamed Fleet
        ("eggs", janet),   # Janet is not allergic to eggs
        ("mold", janet),   # Janet is not allergic to mold
        ("lemon", janet),  # Janet is not surnamed Lemon
    }

    solver = Exact()

    # Exact identifies its variables by name.
    # Each name is the friend who has it. Debra is allergic to ragweed.
    for name in names:
        lower, upper = (debra, debra) if name == "ragweed" else (0, n - 1)
        solver.addVariable(name, lower, upper)

    # is_friend[name][f] is 1 when friend f has the name, and 0 when not. A ruled-out
    # friend is fixed at 0.
    is_friend = {}
    for name in names:
        is_friend[name] = []
        for f in range(n):
            flag = f"{name}_is_{f}"
            solver.addVariable(flag, 0, 0 if (name, f) in ruled_out else 1)
            is_friend[name].append(flag)

    # Each name belongs to exactly one friend, and the name's value is that friend.
    for name in names:
        solver.addConstraint([(1, flag) for flag in is_friend[name]], True, 1, True, 1)
        solver.addConstraint([(f, is_friend[name][f]) for f in range(1, n)] + [(-1, name)],
                             True, 0, True, 0)

    # Each friend has exactly one allergy and exactly one surname.
    for group in (foods, surnames):
        for f in range(n):
            solver.addConstraint([(1, is_friend[name][f]) for name in group], True, 1, True, 1)

    # Baxter is allergic to eggs.
    solver.addConstraint([(1, "eggs"), (-1, "baxter")], True, 0, True, 0)

    return solver, {name: name for name in names}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

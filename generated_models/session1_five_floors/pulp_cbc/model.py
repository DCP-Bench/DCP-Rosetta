# session1_five_floors: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install pulp numpy`) with:
#   python session1_five_floors.py

import pulp


def create_model(instance):
    """Baker, Cooper, Fletcher, Miller and Smith live on different floors of a
    five-floor apartment house; find their floors from the stated clues."""
    people = ["B", "C", "F", "M", "S"]  # Baker, Cooper, Fletcher, Miller, Smith
    floors = range(1, 6)                # the floor numbers 1 to 5

    # The floors each person can live on. Baker is not on the fifth floor, Cooper
    # is not on the first, and Fletcher is on neither the first nor the fifth.
    floors_for = {
        "B": range(1, 5),
        "C": range(2, 6),
        "F": range(2, 5),
        "M": floors,
        "S": floors,
    }

    problem = pulp.LpProblem("five_floors", pulp.LpMinimize)

    # on[x][f] is 1 when person x lives on floor f, and 0 when not
    on = {x: {f: pulp.LpVariable(f"on_{x}_{f}", cat="Binary") for f in floors_for[x]} for x in people}

    # The floor where each person lives
    floor = {x: pulp.lpSum(f * var for f, var in on[x].items()) for x in people}

    # Two people do not live on neighbouring floors.
    def not_neighbours(x, y):
        for f in on[x]:
            for g in on[y]:
                if abs(f - g) == 1:
                    problem.addConstraint(on[x][f] + on[y][g] <= 1)

    # Each person lives on exactly one floor.
    for x in people:
        problem += pulp.lpSum(on[x].values()) == 1

    # Everyone lives on a different floor, so each floor has exactly one person.
    for f in floors:
        problem += pulp.lpSum(on[x][f] for x in people if f in on[x]) == 1

    # Miller lives on a higher floor than Cooper.
    problem += floor["M"] >= floor["C"] + 1

    # Smith does not live on a floor next to Fletcher's.
    not_neighbours("S", "F")

    # Fletcher does not live on a floor next to Cooper's.
    not_neighbours("F", "C")

    # No objective: any arrangement of floors that fits the clues is an answer.
    return problem, floor


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

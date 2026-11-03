# zebra: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install pulp numpy`) with:
#   python zebra.py

import pulp


def create_model(instance):
    """The Zebra puzzle: five houses in a row, each with a different color,
    inhabitant nationality, pet, drink and job, fixed by a list of clues. Find the
    house of every color, nationality, job, pet and drink."""
    n_houses = 5  # the five houses in the row
    houses = range(n_houses)

    # The five groups of attributes, five items in each.
    groups = {
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
    }

    problem = pulp.LpProblem("zebra", pulp.LpMinimize)

    # in_house[item][h] is 1 when the item belongs to house h.
    in_house = {item: [pulp.LpVariable(f"in_house_{item}_{h}", cat="Binary") for h in houses]
                for items in groups.values() for item in items}

    # Each item belongs to exactly one house.
    for items in groups.values():
        for item in items:
            problem += pulp.lpSum(in_house[item]) == 1

    # Each house has exactly one item from each group.
    for items in groups.values():
        for h in houses:
            problem += pulp.lpSum(in_house[item][h] for item in items) == 1

    def same_house(x, y):
        """x and y belong to the same house."""
        for h in houses:
            problem.addConstraint(in_house[x][h] == in_house[y][h])

    def right_of(x, y):
        """x belongs to the house immediately to the right of y's house."""
        problem.addConstraint(in_house[x][0] == 0)
        for h in range(n_houses - 1):
            problem.addConstraint(in_house[x][h + 1] == in_house[y][h])

    def next_to(x, y):
        """x and y belong to neighbouring houses."""
        for h in houses:
            problem.addConstraint(
                in_house[x][h] <= pulp.lpSum(in_house[y][g] for g in (h - 1, h + 1)
                                             if 0 <= g < n_houses))

    same_house("painter", "horse")       # the painter owns the horse
    same_house("diplomat", "coffee")     # the diplomat drinks coffee
    same_house("white", "milk")          # the one who drinks milk lives in the white house
    same_house("spain", "painter")       # the Spaniard is a painter
    same_house("england", "red")         # the Englishman lives in the red house
    same_house("snails", "sculptor")     # the snails are owned by the sculptor
    right_of("red", "green")             # the green house is immediately left of the red one
    right_of("norway", "blue")           # the Norwegian lives immediately right of the blue house
    same_house("doctor", "milk")         # the doctor drinks milk
    same_house("japan", "diplomat")      # the diplomat is Japanese
    same_house("norway", "zebra")        # the Norwegian owns the zebra
    next_to("green", "white")            # the green house is next to the white one
    next_to("horse", "diplomat")         # the horse is owned by the neighbour of the diplomat

    # The Italian lives in the red, white or green house.
    for h in houses:
        problem += (in_house["italy"][h]
                    <= in_house["red"][h] + in_house["white"][h] + in_house["green"][h])

    # The house of each color, nationality, job, pet and drink.
    return problem, {key: [pulp.lpSum(h * flag for h, flag in enumerate(in_house[item]))
                           for item in items]
                     for key, items in groups.items()}


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

# zebra: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/zebra.html
# Run it (after `pip install exact numpy`) with:
#   python zebra.py

from exact import Exact


def create_model(instance):
    """The Zebra puzzle: five houses in a row, each with a different color,
    inhabitant nationality, pet, drink and job, fixed by a list of clues. Find the
    house number (0 to 4, left to right) of every color, nationality, job, pet and
    drink."""
    n_houses = 5  # the houses, numbered 0 (leftmost) to 4 (rightmost)
    kinds = {  # the five items of each kind, one per house
        "colors": ["yellow", "green", "red", "white", "blue"],
        "nations": ["italy", "spain", "japan", "england", "norway"],
        "jobs": ["painter", "sculptor", "diplomat", "pianist", "doctor"],
        "pets": ["cat", "zebra", "bear", "snails", "horse"],
        "drinks": ["milk", "water", "tea", "coffee", "juice"],
    }

    solver = Exact()

    # Exact identifies its variables by name.
    # Each item is a variable holding the number of its house. is_in[item][h] is 1 when the
    # item is in house h, and 0 when not.
    is_in = {}
    for items in kinds.values():
        for item in items:
            solver.addVariable(item, 0, n_houses - 1)
            is_in[item] = [f"{item}_in_{h}" for h in range(n_houses)]
            for name in is_in[item]:
                solver.addVariable(name, 0, 1)
            # Each item is in exactly one house, and its number is that house.
            solver.addConstraint([(1, name) for name in is_in[item]], True, 1, True, 1)
            solver.addConstraint([(h, is_in[item][h]) for h in range(1, n_houses)] +
                                 [(-1, item)], True, 0, True, 0)
        # All items of one kind are in different houses: every house holds exactly one of them.
        for h in range(n_houses):
            solver.addConstraint([(1, is_in[item][h]) for item in items], True, 1, True, 1)

    def same_house(x, y):
        # x and y are in the same house.
        solver.addConstraint([(1, x), (-1, y)], True, 0, True, 0)

    def immediately_left(x, y):
        # x is in the house directly to the left of y.
        solver.addConstraint([(1, x), (-1, y)], True, -1, True, -1)

    def neighbours(x, y):
        # x and y are in neighbouring houses: when x is in house h, y is in house h - 1 or h + 1.
        for h in range(n_houses):
            next_door = [(1, is_in[y][g]) for g in (h - 1, h + 1) if 0 <= g < n_houses]
            solver.addConstraint(next_door + [(-1, is_in[x][h])], True, 0)

    # the painter owns the horse
    same_house("painter", "horse")
    # the diplomat drinks coffee
    same_house("diplomat", "coffee")
    # the one who drinks milk lives in the white house
    same_house("milk", "white")
    # the Spaniard is a painter
    same_house("spain", "painter")
    # the Englishman lives in the red house
    same_house("england", "red")
    # the snails are owned by the sculptor
    same_house("snails", "sculptor")
    # the green house is immediately on the left of the red one
    immediately_left("green", "red")
    # the Norwegian lives immediately on the right of the blue house
    immediately_left("blue", "norway")
    # the doctor drinks milk
    same_house("doctor", "milk")
    # the diplomat is Japanese
    same_house("japan", "diplomat")
    # the Norwegian owns the zebra
    same_house("norway", "zebra")
    # the green house is next to the white one
    neighbours("green", "white")
    # the horse is owned by the neighbor of the diplomat
    neighbours("horse", "diplomat")
    # the Italian either lives in the red, white or green house
    for h in range(n_houses):
        solver.addConstraint([(1, is_in[c][h]) for c in ("red", "white", "green")] +
                             [(-1, is_in["italy"][h])], True, 0)

    return solver, kinds


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

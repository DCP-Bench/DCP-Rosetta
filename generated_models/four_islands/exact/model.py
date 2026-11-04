# four_islands: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install exact numpy`) with:
#   python four_islands.py

from exact import Exact


def create_model(instance):
    """Four islands sit at the corners of a square map, A B over C D, joined by bridges.
    Each island has its own name, export and tourist attraction. Find the corner of each
    island, export and attraction from six clues."""
    n_islands = 4  # the islands, one on each map corner
    A, B, C, D = range(n_islands)  # the corners: A north-west, B north-east, C south-west, D south-east

    # The names of the islands, exports and attractions.
    kinds = {
        "island": ["Pwana", "Quero", "Rayou", "Skern"],
        "export": ["alabaster", "bananas", "coconuts", "durian_fruit"],
        "attraction": ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"],
    }

    solver = Exact()

    # at[item][pos] is 1 when the item sits on corner pos.
    at = {}

    # Exact identifies its variables by name.
    # A clue holds when one of its options is chosen. Choosing an option puts every
    # (item, corner) pair in it in place.
    def one_of(label, options):
        chosen = []  # the options of this clue, one of which is chosen
        for k, option in enumerate(options):
            pick = f"{label}_option_{k}"  # 1 when this option is chosen
            solver.addVariable(pick, 0, 1)
            chosen.append((1, pick))
            for item, pos in option:
                solver.addConstraint([(1, at[item][pos]), (-1, pick)], True, 0)
        solver.addConstraint(chosen, True, 1)

    for items in kinds.values():
        for item in items:
            # Each name is a variable holding the corner its item sits on.
            solver.addVariable(item, 0, n_islands - 1)
            at[item] = [f"{item}_at_{pos}" for pos in range(n_islands)]
            for place in at[item]:
                solver.addVariable(place, 0, 1)
            # Each item sits on exactly one corner.
            solver.addConstraint([(1, place) for place in at[item]], True, 1, True, 1)
            # The item's variable is the corner it sits on.
            solver.addConstraint([(pos, at[item][pos]) for pos in range(1, n_islands)] +
                                 [(-1, item)], True, 0, True, 0)
        # The items of one kind sit on different corners.
        for pos in range(n_islands):
            solver.addConstraint([(1, at[item][pos]) for item in items], True, 1, True, 1)

    pwana, quero, rayou, skern = kinds["island"]
    alabaster, bananas, coconuts, durian_fruit = kinds["export"]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = kinds["attraction"]

    # 1. The island noted for its koala preserve is due south of Pwana.
    one_of("clue1", [[(pwana, A), (koala_preserve, C)],
                     [(pwana, B), (koala_preserve, D)]])
    # 2. The island with the largest alabaster quarry is due west of Quero.
    one_of("clue2", [[(alabaster, A), (quero, B)],
                     [(alabaster, C), (quero, D)]])
    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    one_of("clue3", [[(durian_fruit, A), (resort_hotel, B)],
                     [(durian_fruit, C), (resort_hotel, D)]])
    # 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
    one_of("clue4", [[(skern, A), (jai_alai_stadium, C)],
                     [(skern, C), (jai_alai_stadium, A)],
                     [(skern, B), (jai_alai_stadium, D)],
                     [(skern, D), (jai_alai_stadium, B)]])
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    one_of("clue5", [[(rayou, A), (bananas, B)],
                     [(rayou, B), (bananas, A)],
                     [(rayou, C), (bananas, D)],
                     [(rayou, D), (bananas, C)]])
    # 6. The islands with the ice skating rink and the jai alai stadium have no bridge between
    #    them, so they sit diagonally opposite each other.
    one_of("clue6", [[(ice_skating_rink, A), (jai_alai_stadium, D)],
                     [(ice_skating_rink, D), (jai_alai_stadium, A)],
                     [(ice_skating_rink, B), (jai_alai_stadium, C)],
                     [(ice_skating_rink, C), (jai_alai_stadium, B)]])

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

# four_islands: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install cvc5 numpy`) with:
#   python four_islands.py

import cvc5.pythonic as c5


def create_model(instance):
    """Four islands, A and B on the top row and C and D below, with bridges A-B, A-C, B-D and C-D.
    Each island has its own name, primary export and tourist attraction. Find the name, export
    and attraction of each island on the map, given six clues."""
    # The puzzle gives its own map and clues, so instance is not used.

    # The four positions on the map: A, B, C and D.
    a, b, c, d = range(4)

    # Pairs (x, y) where y is due south of x.
    south = [(a, c), (b, d)]
    # Pairs (x, y) where x is due west of y.
    west = [(a, b), (c, d)]
    # Pairs (x, y) where x is due east of y.
    east = [(b, a), (d, c)]
    # Pairs (x, y) joined by a north-south bridge, in either order.
    north_south = [(a, c), (c, a), (b, d), (d, b)]
    # Pairs (x, y) joined by an east-west bridge, in either order.
    east_west = [(a, b), (b, a), (c, d), (d, c)]
    # Pairs (x, y) on a diagonal of the map, so no bridge joins them.
    diagonal = [(a, d), (d, a), (b, c), (c, b)]

    # True when the positions x and y form one of the given pairs.
    def in_pairs(x, y, pairs):
        return c5.Or([c5.And(x == p, y == q) for p, q in pairs])

    # The map position of each island: Pwana, Quero, Rayou and Skern.
    island = c5.Ints(["island_pwana", "island_quero", "island_rayou", "island_skern"])
    pwana, quero, rayou, skern = island
    # The map position of the island that exports each product: alabaster, bananas,
    # coconuts and durian fruit.
    export = c5.Ints(["export_alabaster", "export_bananas", "export_coconuts", "export_durian_fruit"])
    alabaster, bananas, _, durian_fruit = export
    # The map position of the island with each tourist attraction: resort hotel, ice skating
    # rink, jai alai stadium and koala preserve.
    attraction = c5.Ints(["attraction_resort_hotel", "attraction_ice_skating_rink",
                          "attraction_jai_alai_stadium", "attraction_koala_preserve"])
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # Each island, export and attraction is at a position from A to D.
    bounds = [v >= 0 for v in island + export + attraction] + [v <= 3 for v in island + export + attraction]

    solver = c5.Solver()

    solver.add(bounds + [
        # The islands, the exports and the attractions each take four different positions.
        c5.Distinct(island),
        c5.Distinct(export),
        c5.Distinct(attraction),
        # The island noted for its koala preserve is due south of Pwana.
        in_pairs(pwana, koala_preserve, south),
        # The island with the largest alabaster quarry is due west of Quero.
        in_pairs(alabaster, quero, west),
        # The island with the resort hotel is due east of the one that exports durian fruit.
        in_pairs(resort_hotel, durian_fruit, east),
        # Skern and the island with the jai alai stadium are connected by a north-south bridge.
        in_pairs(skern, jai_alai_stadium, north_south),
        # Rayou and the island that exports bananas are connected by an east-west bridge.
        in_pairs(rayou, bananas, east_west),
        # The ice skating rink and the jai alai stadium are not connected by a bridge.
        in_pairs(ice_skating_rink, jai_alai_stadium, diagonal),
    ])

    outputs = {"island": island, "export": export, "attraction": attraction}
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

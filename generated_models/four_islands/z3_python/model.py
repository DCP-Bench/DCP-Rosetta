# four_islands: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install z3-solver numpy`) with:
#   python four_islands.py

import z3


def create_model(instance):
    """Four islands, laid out as A B over C D with bridges A-B, C-D, A-C and B-D. Each island
    has a different name, primary export and tourist attraction. Find the name, export and
    attraction of each island on the map, given six clues."""
    n_islands = 4
    A, B, C, D = range(n_islands)  # map positions: A top left, B top right, C bottom left, D bottom right

    # island[i] is the map position of Pwana, Quero, Rayou and Skern, in that order
    island = [z3.Int(f"island_{i}") for i in range(n_islands)]
    pwana, quero, rayou, skern = island
    # export[i] is the map position of the island exporting alabaster, bananas, coconuts and
    # durian fruit, in that order
    export = [z3.Int(f"export_{i}") for i in range(n_islands)]
    alabaster, bananas, coconuts, durian_fruit = export
    # attraction[i] is the map position of the island with the resort hotel, the ice skating
    # rink, the jai alai stadium and the koala preserve, in that order
    attraction = [z3.Int(f"attraction_{i}") for i in range(n_islands)]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # (north, south) pairs of positions: the second lies due south of the first.
    south_of = [(A, C), (B, D)]
    # (west, east) pairs of positions: the second lies due east of the first.
    east_of = [(A, B), (C, D)]
    # Pairs joined by a north-south bridge, in either order.
    north_south_bridge = south_of + [(s, n) for n, s in south_of]
    # Pairs joined by an east-west bridge, in either order.
    east_west_bridge = east_of + [(e, w) for w, e in east_of]
    # Diagonal pairs, which no bridge joins, in either order.
    no_bridge = [(A, D), (D, A), (B, C), (C, B)]

    def related(first, second, pairs):
        # first and second take one of the given pairs of map positions, in that order
        return z3.Or([z3.And(first == a, second == b) for a, b in pairs])

    solver = z3.Solver()

    # Every island, export and attraction is at one of the four map positions.
    solver.add([z3.And(0 <= v, v <= n_islands - 1) for v in island + export + attraction])

    # The four islands are at four different positions, and likewise the exports and the attractions.
    solver.add(z3.Distinct(island), z3.Distinct(export), z3.Distinct(attraction))

    # The island noted for its koala preserve is due south of Pwana.
    solver.add(related(pwana, koala_preserve, south_of))

    # The island with the largest alabaster quarry is due west of Quero.
    solver.add(related(alabaster, quero, east_of))

    # The island with the resort hotel is due east of the one that exports durian fruit.
    solver.add(related(durian_fruit, resort_hotel, east_of))

    # Skern and the island with the jai alai stadium are connected by a north-south bridge.
    solver.add(related(skern, jai_alai_stadium, north_south_bridge))

    # Rayou and the island that exports bananas are connected by an east-west bridge.
    solver.add(related(rayou, bananas, east_west_bridge))

    # The islands with the ice skating rink and the jai alai stadium are not connected by a bridge.
    solver.add(related(ice_skating_rink, jai_alai_stadium, no_bridge))

    return solver, {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

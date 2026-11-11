# four_islands: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python four_islands.py

from pycsp3 import *


def create_model(instance):
    """Four islands, Pwana, Quero, Rayou and Skern, lie at the map positions A, B, C
    and D: A and B on the top row, C and D on the bottom row, with bridges A-B, C-D,
    A-C and B-D. Each island has a different primary export (alabaster, bananas,
    coconuts, durian fruit) and a different tourist attraction (resort hotel, ice
    skating rink, jai alai stadium, koala preserve). Using the six clues, find the
    map position of each island, of each export and of each attraction."""
    n = 4  # four islands, four exports and four attractions
    A, B, C, D = range(n)  # map positions, encoded as A=0, B=1, C=2, D=3
    # Names for the indices of the island, export and attraction lists, in the order the output lists them.
    pwana, quero, rayou, skern = range(n)
    alabaster, bananas, coconuts, durian_fruit = range(n)
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = range(n)

    # Pairs (x, y) of positions where x is due west of y.
    west_of = [(A, B), (C, D)]
    # Pairs (x, y) of positions where y is due south of x.
    south_of = [(A, C), (B, D)]
    # Pairs of positions joined by an east-west bridge, in either order.
    east_west_bridge = [(A, B), (B, A), (C, D), (D, C)]
    # Pairs of positions joined by a north-south bridge, in either order.
    north_south_bridge = [(A, C), (C, A), (B, D), (D, B)]
    # Pairs of positions with no bridge between them (the two diagonals).
    no_bridge = [(A, D), (D, A), (B, C), (C, B)]

    # island[i] is the map position of island i.
    island = VarArray(size=n, dom=range(n))
    # export[e] is the map position of the island whose export is e.
    export = VarArray(size=n, dom=range(n))
    # attraction[a] is the map position of the island with tourist attraction a.
    attraction = VarArray(size=n, dom=range(n))

    satisfy(
        # The four islands are on four different positions.
        AllDifferent(island),
        # Each export belongs to a different island.
        AllDifferent(export),
        # Each attraction belongs to a different island.
        AllDifferent(attraction),
        # The island with the koala preserve is due south of Pwana.
        Table(scope=[island[pwana], attraction[koala_preserve]], supports=south_of),
        # The island with the alabaster quarry is due west of Quero.
        Table(scope=[export[alabaster], island[quero]], supports=west_of),
        # The island with the resort hotel is due east of the island exporting durian fruit.
        Table(scope=[export[durian_fruit], attraction[resort_hotel]], supports=west_of),
        # Skern and the island with the jai alai stadium are connected by a north-south bridge.
        Table(scope=[island[skern], attraction[jai_alai_stadium]], supports=north_south_bridge),
        # Rayou and the island exporting bananas are connected by an east-west bridge.
        Table(scope=[island[rayou], export[bananas]], supports=east_west_bridge),
        # The islands with the ice skating rink and the jai alai stadium are not connected by a bridge.
        Table(scope=[attraction[ice_skating_rink], attraction[jai_alai_stadium]], supports=no_bridge),
    )

    return {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

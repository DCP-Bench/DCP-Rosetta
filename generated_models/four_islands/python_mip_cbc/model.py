# four_islands: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install mip numpy`) with:
#   python four_islands.py

import mip

# The squares of the map: A top left, B top right, C bottom left, D bottom right.
A, B, C, D = range(4)

# The square due south of each square, and the squares due east and due west of each square.
SOUTH = {A: [C], B: [D]}
EAST = {A: [B], C: [D]}
WEST = {B: [A], D: [C]}
# The squares joined to each square by an east-west bridge, by a north-south bridge, and by any bridge.
EW_BRIDGE = {A: [B], B: [A], C: [D], D: [C]}
NS_BRIDGE = {A: [C], C: [A], B: [D], D: [B]}
BRIDGED = {A: [B, C], B: [A, D], C: [A, D], D: [B, C]}


def place_each(model, tag):
    # where[k][p] is 1 when item k is on square p. Each item is on one square,
    # and each square holds one item.
    where = [[model.add_var(f"{tag}_{k}_{p}", var_type=mip.BINARY) for p in range(4)]
             for k in range(4)]
    for k in range(4):
        model += mip.xsum(where[k]) == 1
    for p in range(4):
        model += mip.xsum(where[k][p] for k in range(4)) == 1
    return where


def related(model, clue_at, item_at, mapping):
    # If the item is on square p, the clue item is on one of the squares mapping[p].
    for p in range(4):
        model += item_at[p] <= mip.xsum(clue_at[q] for q in mapping.get(p, []))


def create_model(instance):
    """Four islands, laid out as A B over C D, with bridges A-B, C-D, A-C and B-D. Each island
    has a different name, primary export and tourist attraction. Find the name, export and
    attraction of each island on the map, given six clues."""
    model = mip.Model(solver_name="CBC")

    # island_at[i][p] is 1 when the island with name i is on square p.
    island_at = place_each(model, "island")
    # export_at[k][p] is 1 when the island on square p exports item k.
    export_at = place_each(model, "export")
    # attraction_at[k][p] is 1 when the island on square p has attraction k.
    attraction_at = place_each(model, "attraction")

    # The square of each island: Pwana, Quero, Rayou and Skern.
    island = [model.add_var(f"island_{i}", lb=0, ub=3, var_type=mip.INTEGER) for i in range(4)]
    # The square of the island exporting alabaster, bananas, coconuts and durian fruit.
    export = [model.add_var(f"export_{k}", lb=0, ub=3, var_type=mip.INTEGER) for k in range(4)]
    # The square of the island with the resort hotel, ice skating rink, jai alai stadium and koala preserve.
    attraction = [model.add_var(f"attraction_{k}", lb=0, ub=3, var_type=mip.INTEGER) for k in range(4)]

    # Each island, export and attraction is on the square its placement gives.
    for i in range(4):
        model += island[i] == mip.xsum(p * island_at[i][p] for p in range(4))
    for k in range(4):
        model += export[k] == mip.xsum(p * export_at[k][p] for p in range(4))
        model += attraction[k] == mip.xsum(p * attraction_at[k][p] for p in range(4))

    # Pwana, Quero, Rayou, Skern.
    pwana, quero, rayou, skern = island
    # Alabaster, bananas, coconuts, durian fruit.
    alabaster, bananas, coconuts, durian_fruit = export
    # Resort hotel, ice skating rink, jai alai stadium, koala preserve.
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # The island noted for its koala preserve is due south of Pwana.
    related(model, attraction_at[3], island_at[0], SOUTH)

    # The island with the largest alabaster quarry is due west of Quero.
    related(model, export_at[0], island_at[1], WEST)

    # The island with the resort hotel is due east of the one that exports durian fruit.
    related(model, attraction_at[0], export_at[3], EAST)

    # Skern and the island with the jai alai stadium are connected by a north-south bridge.
    related(model, attraction_at[2], island_at[3], NS_BRIDGE)

    # Rayou and the island that exports bananas are connected by an east-west bridge.
    related(model, export_at[1], island_at[2], EW_BRIDGE)

    # The islands with the ice skating rink and the jai alai stadium are not connected by a bridge.
    for p in range(4):
        for q in BRIDGED[p]:
            model += attraction_at[1][p] + attraction_at[2][q] <= 1

    outputs = {"island": island, "export": export, "attraction": attraction}
    return model, outputs


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

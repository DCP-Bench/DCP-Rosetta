# four_islands: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python four_islands.py

from pyscipopt import Model, quicksum

# The map is a square with the islands at its corners, numbered 0 = A, 1 = B, 2 = C, 3 = D:
#     A(0) -- B(1)
#      |        |
#     C(2) -- D(3)
# so cell p is in the north row when p < 2 and in the south row when p >= 2, and in the
# west column when p is even and in the east column when p is odd.
# The statement fixes the whole problem: its instance file is empty ([]), and the run
# block passes {} to create_model, which reads nothing from its argument.

# Named items, in the order the statement lists them.
PWANA, QUERO, RAYOU, SKERN = range(4)  # the four islands
ALABASTER, BANANAS, DURIAN = 0, 1, 3  # the primary exports the clues name (coconuts, 2, no clue names)
HOTEL, SKATING_RINK, JAI_ALAI, KOALA = range(4)  # the four tourist attractions


def in_south_row(grid, item):
    """1 when `item` is on the south row of the map (cells 2 and 3), 0 when on the north row."""
    return quicksum(grid[item, p] for p in (2, 3))


def in_east_column(grid, item):
    """1 when `item` is in the east column of the map (cells 1 and 3), 0 when in the west column."""
    return quicksum(grid[item, p] for p in (1, 3))


def create_model(instance):
    """Four islands on a square map each have a different primary export and a different
    tourist attraction. From the clues, find the map cell of each island, of each export
    and of each attraction. The cells are numbered 0 to 3 as on the map above.
    Returns the model and the cell lists as outputs `island`, `export` and `attraction`."""
    model = Model("four_islands")

    # island_at[i, p] is 1 when island i (a row of PWANA..SKERN) is on map cell p.
    # Each island is on one cell, so each row holds one 1 (a one-hot choice of cell).
    island_at = model.addMatrixVar((4, 4), vtype="B", name="island_at")
    # export_at[e, p] is 1 when export e (a row of ALABASTER..DURIAN) belongs to the island on cell p.
    export_at = model.addMatrixVar((4, 4), vtype="B", name="export_at")
    # attraction_at[a, p] is 1 when attraction a (a row of HOTEL..KOALA) is on the island on cell p.
    attraction_at = model.addMatrixVar((4, 4), vtype="B", name="attraction_at")

    # Each item is on exactly one cell (row sums are 1), and each cell holds exactly one item
    # of each kind (column sums are 1). SCIP has no all-different, so the sums state it.
    model.addMatrixCons(island_at.sum(axis=1) == 1)
    model.addMatrixCons(island_at.sum(axis=0) == 1)
    model.addMatrixCons(export_at.sum(axis=1) == 1)
    model.addMatrixCons(export_at.sum(axis=0) == 1)
    model.addMatrixCons(attraction_at.sum(axis=1) == 1)
    model.addMatrixCons(attraction_at.sum(axis=0) == 1)

    # The island with the koala preserve is due south of Pwana: one row lower, same column.
    model.addCons(in_south_row(attraction_at, KOALA) - in_south_row(island_at, PWANA) == 1)
    model.addCons(in_east_column(attraction_at, KOALA) == in_east_column(island_at, PWANA))

    # The island with the largest alabaster quarry is due west of Quero: same row, one column west.
    model.addCons(in_south_row(export_at, ALABASTER) == in_south_row(island_at, QUERO))
    model.addCons(in_east_column(export_at, ALABASTER) + 1 == in_east_column(island_at, QUERO))

    # The island with the resort hotel is due east of the island that exports durian fruit.
    model.addCons(in_south_row(attraction_at, HOTEL) == in_south_row(export_at, DURIAN))
    model.addCons(in_east_column(attraction_at, HOTEL) == in_east_column(export_at, DURIAN) + 1)

    # Skern and the jai alai stadium are joined by a north-south bridge: same column, different rows.
    model.addCons(in_east_column(island_at, SKERN) == in_east_column(attraction_at, JAI_ALAI))
    model.addCons(in_south_row(island_at, SKERN) + in_south_row(attraction_at, JAI_ALAI) == 1)

    # Rayou and the island that exports bananas are joined by an east-west bridge:
    # same row, different columns.
    model.addCons(in_south_row(island_at, RAYOU) == in_south_row(export_at, BANANAS))
    model.addCons(in_east_column(island_at, RAYOU) + in_east_column(export_at, BANANAS) == 1)

    # The ice skating rink and the jai alai stadium are not joined by a bridge. Two different
    # cells on this square are either joined by a bridge or diagonal, so not joined means
    # different rows and different columns.
    model.addCons(in_south_row(attraction_at, SKATING_RINK) + in_south_row(attraction_at, JAI_ALAI) == 1)
    model.addCons(in_east_column(attraction_at, SKATING_RINK) + in_east_column(attraction_at, JAI_ALAI) == 1)

    # The output of each item is its cell: the sum of cell number times its one-hot choice.
    island = [quicksum(p * island_at[i, p] for p in range(4)) for i in range(4)]
    export = [quicksum(p * export_at[e, p] for p in range(4)) for e in range(4)]
    attraction = [quicksum(p * attraction_at[a, p] for p in range(4)) for a in range(4)]

    return model, {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

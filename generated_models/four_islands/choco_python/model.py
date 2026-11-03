# four_islands: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install pychoco numpy`) with:
#   python four_islands.py

from pychoco.model import Model


def create_model(instance):
    """Four islands, A and B on the top row and C and D on the bottom row, joined by bridges
    A-B, C-D, A-C and B-D. Each island has its own name, primary export and tourist
    attraction. Find the name, export and attraction of each island on the map, given six
    clues."""
    # The four positions on the map: A is north of C and west of B; C is west of D; B is north of D.
    A, B, C, D = range(4)

    # (north, south) pairs of positions, the second due south of the first
    south_of = [(A, C), (B, D)]
    # (west, east) pairs of positions, the second due east of the first
    west_of = [(A, B), (C, D)]
    # pairs of positions joined by a north-south bridge, in either order
    north_south_bridge = south_of + [(s, n) for n, s in south_of]
    # pairs of positions joined by an east-west bridge, in either order
    east_west_bridge = west_of + [(e, w) for w, e in west_of]
    # diagonal pairs of positions, which have no bridge between them
    no_bridge = [(A, D), (D, A), (B, C), (C, B)]

    model = Model()

    # The map position of Pwana, Quero, Rayou and Skern.
    island = [model.intvar(0, 3, name=f"island_{k}") for k in range(4)]
    pwana, quero, rayou, skern = island
    # The map position of the island that exports alabaster, bananas, coconuts and durian fruit.
    export = [model.intvar(0, 3, name=f"export_{k}") for k in range(4)]
    alabaster, bananas, coconuts, durian_fruit = export
    # The map position of the island with the resort hotel, the ice skating rink, the jai alai
    # stadium and the koala preserve.
    attraction = [model.intvar(0, 3, name=f"attraction_{k}") for k in range(4)]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    # Each island has its own name, export and attraction.
    for group in (island, export, attraction):
        model.all_different(group).post()

    # 1. The island with the koala preserve is due south of Pwana.
    model.table([pwana, koala_preserve], south_of).post()
    # 2. The island with the alabaster quarry is due west of Quero.
    model.table([alabaster, quero], west_of).post()
    # 3. The island with the resort hotel is due east of the one exporting durian fruit.
    model.table([durian_fruit, resort_hotel], west_of).post()
    # 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
    model.table([skern, jai_alai_stadium], north_south_bridge).post()
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    model.table([rayou, bananas], east_west_bridge).post()
    # 6. The ice skating rink and the jai alai stadium are not connected by a bridge.
    model.table([ice_skating_rink, jai_alai_stadium], no_bridge).post()

    return model, {"island": island, "export": export, "attraction": attraction}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

# four_islands: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install ortools`) with:
#   python four_islands.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Four islands, laid out as A B over C D with bridges A-B, C-D, A-C and B-D. Each island
    has a different name, primary export and tourist attraction. Find the name, export and
    attraction of each island on the map, given six clues."""
    n_islands = 4
    a, b, c, d = range(n_islands)  # map positions: A top left, B top right, C bottom left, D bottom right

    model = cp_model.CpModel()

    # island[i] is the map position of Pwana, Quero, Rayou and Skern, in that order
    island = [model.new_int_var(0, n_islands - 1, f"island_{i}") for i in range(n_islands)]
    pwana, quero, rayou, skern = island
    # export[i] is the map position of the island that exports alabaster, bananas, coconuts
    # and durian fruit, in that order
    export = [model.new_int_var(0, n_islands - 1, f"export_{i}") for i in range(n_islands)]
    alabaster, bananas, coconuts, durian_fruit = export
    # attraction[i] is the map position of the island with the resort hotel, the ice skating
    # rink, the jai alai stadium and the koala preserve, in that order
    attraction = [model.new_int_var(0, n_islands - 1, f"attraction_{i}") for i in range(n_islands)]
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    def one_of(alternatives):
        """An alternative holds when all its (variable, position) pairs hold. One of the
        alternatives holds."""
        picks = []  # picks[k] is true when alternative k holds
        for pairs in alternatives:
            pick = model.new_bool_var(f"alternative_{len(picks)}")
            holds = []  # the checks of the (variable, position) pairs of this alternative
            for variable, value in pairs:
                # check is true when the variable is at the position
                check = model.new_bool_var("")
                model.add(variable == value).only_enforce_if(check)
                model.add(variable != value).only_enforce_if(~check)
                holds.append(check)
            # pick is true exactly when all the checks of its alternative are true
            model.add_bool_and(holds).only_enforce_if(pick)
            model.add_bool_or([~check for check in holds]).only_enforce_if(~pick)
            picks.append(pick)
        # At least one alternative holds.
        model.add_bool_or(picks)

    # Each island has its own name, export and attraction.
    model.add_all_different(island)
    model.add_all_different(export)
    model.add_all_different(attraction)

    # 1. The koala preserve is due south of Pwana: A above C, or B above D.
    one_of([[(pwana, a), (koala_preserve, c)], [(pwana, b), (koala_preserve, d)]])
    # 2. The alabaster quarry is due west of Quero.
    one_of([[(alabaster, a), (quero, b)], [(alabaster, c), (quero, d)]])
    # 3. The resort hotel is due east of the durian fruit exporter.
    one_of([[(durian_fruit, a), (resort_hotel, b)], [(durian_fruit, c), (resort_hotel, d)]])
    # 4. Skern and the jai alai stadium share a north-south bridge.
    one_of([
        [(skern, a), (jai_alai_stadium, c)],
        [(skern, c), (jai_alai_stadium, a)],
        [(skern, b), (jai_alai_stadium, d)],
        [(skern, d), (jai_alai_stadium, b)],
    ])
    # 5. Rayou and the banana exporter share an east-west bridge.
    one_of([
        [(rayou, a), (bananas, b)],
        [(rayou, b), (bananas, a)],
        [(rayou, c), (bananas, d)],
        [(rayou, d), (bananas, c)],
    ])
    # 6. The ice skating rink and the jai alai stadium have no bridge between them, so they
    #    sit on a diagonal.
    one_of([
        [(ice_skating_rink, a), (jai_alai_stadium, d)],
        [(ice_skating_rink, d), (jai_alai_stadium, a)],
        [(ice_skating_rink, b), (jai_alai_stadium, c)],
        [(ice_skating_rink, c), (jai_alai_stadium, b)],
    ])

    return model, {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

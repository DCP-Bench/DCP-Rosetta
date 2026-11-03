# four_islands: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install pulp numpy`) with:
#   python four_islands.py

import pulp


def create_model(instance):
    """Four islands, each with its own name, primary export and tourist attraction.
    Find the name, export and attraction of each island on the map from six clues."""
    n_islands = 4
    A, B, C, D = range(n_islands)  # map positions: A top left, B top right, C bottom left, D bottom right

    groups = {
        "island": ["Pwana", "Quero", "Rayou", "Skern"],
        "export": ["alabaster", "bananas", "coconuts", "durian_fruit"],
        "attraction": ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"],
    }

    problem = pulp.LpProblem("four_islands", pulp.LpMinimize)

    # at[item][pos] is 1 when the name, export or attraction item belongs to the island at map position pos, and 0 when not
    at = {item: [pulp.LpVariable(f"at_{item}_{pos}", cat="Binary") for pos in range(n_islands)]
          for items in groups.values() for item in items}

    # A clue holds when one of its cases holds. A case holds when all its (item, position) pairs hold.
    def one_of(clue, cases):
        picks = []
        for k, case in enumerate(cases):
            pick = pulp.LpVariable(f"clue_{clue}_case_{k}", cat="Binary")
            for item, pos in case:
                problem.addConstraint(pick <= at[item][pos])
            picks.append(pick)
        problem.addConstraint(pulp.lpSum(picks) >= 1)

    # Each name, export and attraction belongs to exactly one island.
    for items in groups.values():
        for item in items:
            problem += pulp.lpSum(at[item]) == 1

    # Each island has exactly one name, one export and one attraction.
    for items in groups.values():
        for pos in range(n_islands):
            problem += pulp.lpSum(at[item][pos] for item in items) == 1

    # The koala preserve is due south of Pwana.
    one_of(1, [[("Pwana", A), ("koala_preserve", C)], [("Pwana", B), ("koala_preserve", D)]])

    # The island with the largest alabaster quarry is due west of Quero.
    one_of(2, [[("alabaster", A), ("Quero", B)], [("alabaster", C), ("Quero", D)]])

    # The island with the resort hotel is due east of the island that exports durian fruit.
    one_of(3, [[("durian_fruit", A), ("resort_hotel", B)], [("durian_fruit", C), ("resort_hotel", D)]])

    # Skern and the island with the jai alai stadium are connected by a north-south bridge.
    one_of(4, [[("Skern", A), ("jai_alai_stadium", C)], [("Skern", C), ("jai_alai_stadium", A)],
               [("Skern", B), ("jai_alai_stadium", D)], [("Skern", D), ("jai_alai_stadium", B)]])

    # Rayou and the island that exports bananas are connected by an east-west bridge.
    one_of(5, [[("Rayou", A), ("bananas", B)], [("Rayou", B), ("bananas", A)],
               [("Rayou", C), ("bananas", D)], [("Rayou", D), ("bananas", C)]])

    # The islands with the ice skating rink and the jai alai stadium are not connected by a bridge.
    one_of(6, [[("ice_skating_rink", A), ("jai_alai_stadium", D)],
               [("ice_skating_rink", D), ("jai_alai_stadium", A)],
               [("ice_skating_rink", B), ("jai_alai_stadium", C)],
               [("ice_skating_rink", C), ("jai_alai_stadium", B)]])

    # The map position of each island, export and attraction, in the order listed above.
    outputs = {
        key: [pulp.lpSum(pos * at[item][pos] for pos in range(n_islands)) for item in items]
        for key, items in groups.items()
    }

    return problem, outputs


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

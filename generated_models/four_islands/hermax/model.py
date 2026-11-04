# four_islands: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install hermax`) with:
#   python four_islands.py

from hermax.model import Model

# Map positions are fixed by the statement and are not instance data:
# A is north-west, B north-east, C south-west, D south-east.
# The bridges are A-B and C-D (east-west), and A-C and B-D (north-south).
A, B, C, D = range(4)


def create_model(instance):
    """Four islands on a 2x2 map (A B / C D), joined by bridges, each with a name, a primary
    export and a tourist attraction. Place every name, export and attraction on the map from
    six clues, so that each island gets a different name, export and attraction."""
    # The clues are fixed by the problem, so the instance carries no data.
    n = 4  # four islands, four exports, four attractions

    m = Model()

    # island[k] is the map position of the island named k: Pwana, Quero, Rayou, Skern
    island = m.int_vector("island", n, 0, n - 1)
    pwana, quero, rayou, skern = (island[k] for k in range(n))

    # export[k] is the map position of the island exporting k:
    # alabaster, bananas, coconuts, durian fruit
    export = m.int_vector("export", n, 0, n - 1)
    alabaster, bananas, coconuts, durian_fruit = (export[k] for k in range(n))

    # attraction[k] is the map position of the island with attraction k:
    # resort hotel, ice skating rink, jai alai stadium, koala preserve
    attraction = m.int_vector("attraction", n, 0, n - 1)
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = (attraction[k] for k in range(n))

    # Each island has a different name, export and attraction, so each vector is a permutation.
    m &= island.all_different()
    m &= export.all_different()
    m &= attraction.all_different()

    # 1. The island with the koala preserve is due south of Pwana:
    #    Pwana at A and koala at C, or Pwana at B and koala at D.
    m &= m.table([pwana, koala_preserve], allowed=[(A, C), (B, D)])

    # 2. The island with the alabaster quarry is due west of Quero:
    #    alabaster at A and Quero at B, or alabaster at C and Quero at D.
    m &= m.table([alabaster, quero], allowed=[(A, B), (C, D)])

    # 3. The island with the resort hotel is due east of the durian fruit exporter:
    #    durian at A and hotel at B, or durian at C and hotel at D.
    m &= m.table([durian_fruit, resort_hotel], allowed=[(A, B), (C, D)])

    # 4. Skern and the jai alai stadium are joined by a north-south bridge (A-C or B-D).
    m &= m.table([skern, jai_alai_stadium], allowed=[(A, C), (C, A), (B, D), (D, B)])

    # 5. Rayou and the banana exporter are joined by an east-west bridge (A-B or C-D).
    m &= m.table([rayou, bananas], allowed=[(A, B), (B, A), (C, D), (D, C)])

    # 6. The ice skating rink and the jai alai stadium are not joined by a bridge,
    #    so they sit on diagonally opposite corners (A-D or B-C).
    m &= m.table([ice_skating_rink, jai_alai_stadium], allowed=[(A, D), (D, A), (B, C), (C, B)])

    # The problem asks for the placement only; there is no objective to optimise.
    return m, {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

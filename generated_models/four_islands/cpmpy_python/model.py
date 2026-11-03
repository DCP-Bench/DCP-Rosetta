# four_islands: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/four_islands.html
# Run it (after `pip install cpmpy`) with:
#   python four_islands.py

import cpmpy as cp


def create_model(instance):
    """Four islands, laid out as A B over C D with bridges A-B, C-D, A-C and B-D, each have a
    different name, primary export and tourist attraction. Find the name, export and
    attraction of each island on the map, given six clues."""
    # The puzzle states its own map and clues, so instance is unused.
    # Every variable holds a map position: A=0, B=1, C=2, D=3.
    n = 4
    a, b, c, d = range(n)

    # island[i] is the map position of Pwana, Quero, Rayou, Skern (in that order).
    island = cp.intvar(0, n - 1, shape=n, name="island")
    pwana, quero, rayou, skern = island
    # export[i] is the map position of the island exporting alabaster, bananas, coconuts,
    # durian fruit (in that order).
    export = cp.intvar(0, n - 1, shape=n, name="export")
    alabaster, bananas, coconuts, durian_fruit = export
    # attraction[i] is the map position of the island with the resort hotel, ice skating
    # rink, jai alai stadium, koala preserve (in that order).
    attraction = cp.intvar(0, n - 1, shape=n, name="attraction")
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = attraction

    model = cp.Model()

    # The islands, the exports and the attractions are all different.
    model.add(cp.AllDifferent(island))
    model.add(cp.AllDifferent(export))
    model.add(cp.AllDifferent(attraction))

    # 1. The koala preserve is due south of Pwana: A above C, or B above D.
    model.add(((pwana == a) & (koala_preserve == c)) | ((pwana == b) & (koala_preserve == d)))
    # 2. The alabaster quarry is due west of Quero.
    model.add(((alabaster == a) & (quero == b)) | ((alabaster == c) & (quero == d)))
    # 3. The resort hotel is due east of the durian fruit exporter.
    model.add(((durian_fruit == a) & (resort_hotel == b)) | ((durian_fruit == c) & (resort_hotel == d)))
    # 4. Skern and the jai alai stadium share a north-south bridge.
    model.add(((skern == a) & (jai_alai_stadium == c)) | ((skern == c) & (jai_alai_stadium == a))
              | ((skern == b) & (jai_alai_stadium == d)) | ((skern == d) & (jai_alai_stadium == b)))
    # 5. Rayou and the banana exporter share an east-west bridge.
    model.add(((rayou == a) & (bananas == b)) | ((rayou == b) & (bananas == a))
              | ((rayou == c) & (bananas == d)) | ((rayou == d) & (bananas == c)))
    # 6. The ice skating rink and the jai alai stadium have no bridge between them,
    #    so they sit on a diagonal.
    model.add(((ice_skating_rink == a) & (jai_alai_stadium == d)) | ((ice_skating_rink == d) & (jai_alai_stadium == a))
              | ((ice_skating_rink == b) & (jai_alai_stadium == c)) | ((ice_skating_rink == c) & (jai_alai_stadium == b)))

    return model, {"island": island, "export": export, "attraction": attraction}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

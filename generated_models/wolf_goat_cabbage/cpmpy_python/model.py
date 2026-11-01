# wolf_goat_cabbage: a CPMpy model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

import cpmpy as cp


def create_model(instance):
    """A farmer with a wolf, a goat and a cabbage must cross a river by boat. The
    boat carries only the farmer and a single item, and if left unattended
    together the wolf eats the goat and the goat eats the cabbage. Find a
    crossing in which nothing is eaten."""
    stage = instance["stage"]  # the number of stages: positions are recorded at stages 0 .. stage-1

    # Each variable is 0 when the item is on the starting shore and 1 on the
    # destination shore, for every stage.
    wolf_pos = cp.boolvar(shape=stage, name="wolf_pos")
    goat_pos = cp.boolvar(shape=stage, name="goat_pos")
    cabbage_pos = cp.boolvar(shape=stage, name="cabbage_pos")
    # boat_pos is the shore of the boat (and so of the farmer) at each stage
    boat_pos = cp.boolvar(shape=stage, name="boat_pos")

    model = cp.Model()

    # Everything starts on the starting shore.
    model.add(boat_pos[0] == 0)
    model.add(wolf_pos[0] == 0)
    model.add(goat_pos[0] == 0)
    model.add(cabbage_pos[0] == 0)

    # The boat crosses the river at every stage.
    model.add(boat_pos[1:] != boat_pos[:-1])

    # Everything ends on the destination shore.
    model.add(boat_pos[-1] == 1)
    model.add(wolf_pos[-1] == 1)
    model.add(goat_pos[-1] == 1)
    model.add(cabbage_pos[-1] == 1)

    # The wolf and the goat are never left alone together: if they share a shore,
    # the boat (with the farmer) is on it too.
    model.add((goat_pos != wolf_pos) | (boat_pos == wolf_pos))
    # Likewise the goat and the cabbage.
    model.add((goat_pos != cabbage_pos) | (boat_pos == goat_pos))

    # The boat carries at most one item per crossing: between two consecutive
    # stages at most one of the three changes shore.
    moved = (wolf_pos[1:] != wolf_pos[:-1]) \
        + (goat_pos[1:] != goat_pos[:-1]) \
        + (cabbage_pos[1:] != cabbage_pos[:-1])
    model.add(moved <= 1)

    return model, {
        "wolf_pos": wolf_pos,
        "goat_pos": goat_pos,
        "cabbage_pos": cabbage_pos,
        "boat_pos": boat_pos,
    }


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

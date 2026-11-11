# wolf_goat_cabbage: a PyCSP3 model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from pycsp3 import *


def create_model(instance):
    """The wolf, goat and cabbage problem is a river crossing puzzle.
    A farmer with a wolf, a goat, and a cabbage must cross a river by boat. The boat can carry only the farmer
    and a single item. If left unattended together, the wolf would eat the goat, or the goat would eat the cabbage.
    How can they cross the river without anything being eaten?
    The crossing takes the given number of stages. At the first stage everything is on the starting shore, at the last
    stage everything is on the destination shore, and the boat, with the farmer, changes shore from each stage to the next."""
    n_stages = instance["stage"]  # the number of stages of the crossing
    first = 0  # index of the first stage
    last = n_stages - 1  # index of the last stage
    n_crossings = n_stages - 1  # the crossings from one stage to the next

    # Each position is a shore: 0 is the starting shore, 1 is the destination shore.
    # wolf_pos[t] is the shore of the wolf at stage t.
    wolf_pos = VarArray(size=n_stages, dom={0, 1})
    # goat_pos[t] is the shore of the goat at stage t.
    goat_pos = VarArray(size=n_stages, dom={0, 1})
    # cabbage_pos[t] is the shore of the cabbage at stage t.
    cabbage_pos = VarArray(size=n_stages, dom={0, 1})
    # boat_pos[t] is the shore of the boat, with the farmer, at stage t.
    boat_pos = VarArray(size=n_stages, dom={0, 1})

    # The three items: the wolf, the goat and the cabbage.
    items = [wolf_pos, goat_pos, cabbage_pos]

    satisfy(
        # At the first stage everything is on the starting shore.
        wolf_pos[first] == 0,
        goat_pos[first] == 0,
        cabbage_pos[first] == 0,
        boat_pos[first] == 0,

        # At the last stage everything is on the destination shore.
        wolf_pos[last] == 1,
        goat_pos[last] == 1,
        cabbage_pos[last] == 1,
        boat_pos[last] == 1,

        # The boat, with the farmer, changes shore from each stage to the next.
        [boat_pos[t] != boat_pos[t + 1] for t in range(n_crossings)],

        # The boat carries the farmer and at most one item, so at most one item changes shore in a crossing.
        [Sum(item[t] != item[t + 1] for item in items) <= 1 for t in range(n_crossings)],

        # An item can only change shore in a crossing when it is on the boat's shore, since the farmer takes it along.
        [imply(item[t] != item[t + 1], item[t] == boat_pos[t]) for item in items for t in range(n_crossings)],

        # The wolf and the goat are never left alone on a shore without the farmer.
        [imply(wolf_pos[t] == goat_pos[t], boat_pos[t] == wolf_pos[t]) for t in range(n_stages)],

        # The goat and the cabbage are never left alone on a shore without the farmer.
        [imply(goat_pos[t] == cabbage_pos[t], boat_pos[t] == goat_pos[t]) for t in range(n_stages)],
    )

    return {
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

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

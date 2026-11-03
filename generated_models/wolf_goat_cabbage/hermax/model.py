# wolf_goat_cabbage: a hermax (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install hermax`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from itertools import product

from hermax.model import Model


def create_model(instance):
    """Wolf, goat and cabbage: a farmer must ferry a wolf, a goat and a cabbage across a river
    in a boat that carries the farmer and at most one item. Left alone together, the wolf eats
    the goat, or the goat eats the cabbage, so these pairs may never share a shore without the
    farmer. Find a sequence of crossings, stage by stage, that moves everything from the start
    shore to the destination shore, and report for each stage which shore each item and the
    boat are on (False = start shore, True = destination shore)."""
    stages = instance["stage"]  # number of stages, the first and the last included

    m = Model()
    # wolf_pos[i] is True when the wolf is on the destination shore at stage i (likewise for the others)
    wolf_pos = m.bool_vector("wolf_pos", stages)
    goat_pos = m.bool_vector("goat_pos", stages)
    cabbage_pos = m.bool_vector("cabbage_pos", stages)
    # boat_pos[i] is True when the boat, and so the farmer, is on the destination shore at stage i
    boat_pos = m.bool_vector("boat_pos", stages)

    # Everything starts on the start shore ...
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        m &= ~pos[0]
    # ... and everything ends on the destination shore.
    for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos):
        m &= pos[stages - 1]

    # The boat crosses the river at every stage: its shore changes from one stage to the next.
    for i in range(1, stages):
        m &= (boat_pos[i] + boat_pos[i - 1] == 1)

    # Safety at every stage: the wolf may not be alone with the goat, nor the goat with the cabbage.
    # The farmer is the boat, so a pair on one shore is safe only when the boat is on that shore too.
    # The allowed (wolf, goat, cabbage, boat) combinations are those where no dangerous pair is left alone.
    safe_rows = [
        (wolf, goat, cabbage, boat)
        for wolf, goat, cabbage, boat in product((False, True), repeat=4)
        if not (wolf == goat and boat != goat) and not (goat == cabbage and boat != goat)
    ]
    for i in range(stages):
        m &= m.table([wolf_pos[i], goat_pos[i], cabbage_pos[i], boat_pos[i]], allowed=safe_rows)

    # Each crossing carries the farmer and at most one of the wolf, goat and cabbage.
    for i in range(stages - 1):
        # moved[k] is True when item k (wolf, goat, cabbage) crosses between stages i and i + 1
        moved = m.bool_vector(f"moved_{i}", 3)
        for k, pos in enumerate((wolf_pos, goat_pos, cabbage_pos)):
            # an item crosses exactly when its shore changes between the two stages
            m &= (pos[i] + pos[i + 1] == 1).iff(moved[k])
            # an item can only cross from the shore the boat is on
            m &= (pos[i] + boat_pos[i] != 1).only_if(moved[k])
        # at most one item crosses per trip
        m &= moved.at_most_one()

    # The model is a satisfaction problem: any sequence of crossings that solves the puzzle is an answer.
    return m, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

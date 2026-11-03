# wolf_goat_cabbage: a SCIP (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from pyscipopt import Model


def create_model(instance):
    """A farmer must take a wolf, a goat and a cabbage across a river. His boat
    carries him and at most one item. Left alone together on a shore, the wolf
    eats the goat and the goat eats the cabbage. Find a sequence of stages, one
    crossing per stage, in which nothing is eaten, and report on which shore the
    wolf, the goat, the cabbage and the boat are at each stage."""
    stages = instance["stage"]  # the number of stages to report, one position per item and per stage

    model = Model("wolf_goat_cabbage")

    # Row indices of the position table: the three items, then the boat.
    WOLF, GOAT, CABBAGE, BOAT = 0, 1, 2, 3

    # side[i, t] is 0 when row i is on the starting shore at stage t and 1 when it is on the
    # destination shore. Each position is one of two shores, so it is binary.
    side = model.addMatrixVar((4, stages), vtype="B", name="side")

    # At stage 0 the farmer and the three items are all on the starting shore, and at the last
    # stage they are all on the destination shore: the statement has them cross the river.
    model.addMatrixCons(side[:, 0] == 0)
    model.addMatrixCons(side[:, stages - 1] == 1)

    # Each stage is one crossing by the boat, so the boat changes shore between consecutive stages.
    model.addMatrixCons(side[BOAT, 1:] + side[BOAT, :-1] == 1)

    # The wolf eats the goat and the goat eats the cabbage. Such a pair may share a shore only
    # with the farmer on it. The first inequality is the starting shore case (both at 0 forces
    # the boat to 0), the second the destination shore case (both at 1 forces the boat to 1).
    for eater, victim in ((WOLF, GOAT), (GOAT, CABBAGE)):
        model.addMatrixCons(side[BOAT] <= side[eater] + side[victim])
        model.addMatrixCons(side[eater] + side[victim] - side[BOAT] <= 1)

    # carried[i, t] is 1 exactly when item i crosses between stage t and stage t + 1, that is when
    # it changes shore.
    carried = model.addMatrixVar((3, stages - 1), vtype="B", name="carried")
    for item in (WOLF, GOAT, CABBAGE):
        for t in range(stages - 1):
            # An XOR with rhs False says the three binaries hold an even number of ones, so
            # carried equals the XOR of the two positions.
            model.addConsXor([side[item, t], side[item, t + 1], carried[item, t]], False)
            # An item that crosses rides in the boat, so it starts on the boat's shore. An
            # indicator cannot take an equality, so the two directions are two indicators.
            model.addConsIndicator(side[item, t] - side[BOAT, t] <= 0, binvar=carried[item, t])
            model.addConsIndicator(side[BOAT, t] - side[item, t] <= 0, binvar=carried[item, t])

    # The boat carries the farmer and at most one item, so at most one item crosses per stage.
    model.addMatrixCons(carried.sum(axis=0) <= 1)

    # There is no objective: the puzzle asks for any sequence that works, so the model is a
    # satisfaction problem.

    outputs = {
        "wolf_pos": side[WOLF],
        "goat_pos": side[GOAT],
        "cabbage_pos": side[CABBAGE],
        "boat_pos": side[BOAT],
    }
    return model, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

# wolf_goat_cabbage: an Exact (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

from exact import Exact


def create_model(instance):
    """A farmer with a wolf, a goat and a cabbage must cross a river by boat. The
    boat carries only the farmer and a single item, and if left unattended
    together the wolf eats the goat and the goat eats the cabbage. Find a
    crossing in which nothing is eaten."""
    stage = instance["stage"]  # the number of stages, from the start to the far shore

    solver = Exact()

    # Exact identifies its variables by name.
    # wolf_pos[s], goat_pos[s], cabbage_pos[s] and boat_pos[s] are 0 when the wolf, the goat,
    # the cabbage or the boat is on the starting shore at stage s, and 1 when it is on the far
    # shore. Everything starts on the starting shore and ends on the far shore.
    names = {}
    for item in ("wolf", "goat", "cabbage", "boat"):
        names[item] = [f"{item}_{s}" for s in range(stage)]
        for s, name in enumerate(names[item]):
            if s == 0:
                solver.addVariable(name, 0, 0)
            elif s == stage - 1:
                solver.addVariable(name, 1, 1)
            else:
                solver.addVariable(name, 0, 1)
    wolf, goat, cabbage, boat = names["wolf"], names["goat"], names["cabbage"], names["boat"]

    # The boat crosses the river between every two consecutive stages.
    for s in range(1, stage):
        solver.addConstraint([(1, boat[s]), (1, boat[s - 1])], True, 1, True, 1)

    # The wolf is never left alone with the goat: when they share a shore, the boat is on that shore too.
    for s in range(stage):
        solver.addConstraint([(1, boat[s]), (-1, goat[s]), (-1, wolf[s])], True, -1)
        solver.addConstraint([(1, goat[s]), (1, wolf[s]), (-1, boat[s])], True, 0)

    # The goat is never left alone with the cabbage, by the same rule.
    for s in range(stage):
        solver.addConstraint([(1, boat[s]), (-1, goat[s]), (-1, cabbage[s])], True, -1)
        solver.addConstraint([(1, goat[s]), (1, cabbage[s]), (-1, boat[s])], True, 0)

    # The boat carries one item at a time, so at most one of the wolf, the goat and the cabbage
    # changes shore between two stages.
    for s in range(stage - 1):
        moved = []
        for item, pos in (("wolf", wolf), ("goat", goat), ("cabbage", cabbage)):
            # moved_<item>_<s> is 1 when the item changes shore from stage s to stage s + 1.
            change = f"moved_{item}_{s}"
            solver.addVariable(change, 0, 1)
            a, b = pos[s], pos[s + 1]
            # The change is 1 exactly when the two shores differ.
            solver.addConstraint([(1, change), (-1, a), (1, b)], True, 0)
            solver.addConstraint([(1, change), (1, a), (-1, b)], True, 0)
            solver.addConstraint([(1, change), (-1, a), (-1, b)], False, 0, True, 0)
            solver.addConstraint([(1, change), (1, a), (1, b)], False, 0, True, 2)
            moved.append((1, change))
        solver.addConstraint(moved, False, 0, True, 1)

    return solver, {"wolf_pos": wolf, "goat_pos": goat, "cabbage_pos": cabbage, "boat_pos": boat}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

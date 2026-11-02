# wolf_goat_cabbage: a Z3 (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

import z3


def create_model(instance):
    """A farmer ferries a wolf, a goat and a cabbage across a river in a boat that carries
    the farmer and one item. Left alone together, the wolf eats the goat and the goat eats
    the cabbage. Find a crossing in which nothing is eaten."""
    stage = instance["stage"]  # the number of stages in the crossing, the first and the last included

    # wolf_pos[i] is true when the wolf is on the destination shore at stage i
    wolf_pos = [z3.Bool(f"wolf_{i}") for i in range(stage)]
    # goat_pos[i] is true when the goat is on the destination shore at stage i
    goat_pos = [z3.Bool(f"goat_{i}") for i in range(stage)]
    # cabbage_pos[i] is true when the cabbage is on the destination shore at stage i
    cabbage_pos = [z3.Bool(f"cabbage_{i}") for i in range(stage)]
    # boat_pos[i] is true when the boat is on the destination shore at stage i
    boat_pos = [z3.Bool(f"boat_{i}") for i in range(stage)]

    solver = z3.Solver()

    # Everything starts on the starting shore.
    solver.add([z3.Not(pos[0]) for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos)])

    # Everything ends on the destination shore.
    solver.add([pos[stage - 1] for pos in (wolf_pos, goat_pos, cabbage_pos, boat_pos)])

    # The boat crosses the river at every stage.
    solver.add([boat_pos[i] != boat_pos[i - 1] for i in range(1, stage)])

    # The wolf and the goat are never left alone: where they share a shore, the boat is there too.
    solver.add([z3.Or(goat_pos[i] != wolf_pos[i], boat_pos[i] == wolf_pos[i]) for i in range(stage)])

    # The goat and the cabbage are never left alone: where they share a shore, the boat is there too.
    solver.add([z3.Or(goat_pos[i] != cabbage_pos[i], boat_pos[i] == goat_pos[i]) for i in range(stage)])

    # The boat carries one item at most: between two stages, at most one of the three changes shore.
    solver.add([
        z3.AtMost(wolf_pos[i] != wolf_pos[i + 1], goat_pos[i] != goat_pos[i + 1],
                  cabbage_pos[i] != cabbage_pos[i + 1], 1)
        for i in range(stage - 1)
    ])

    return solver, {"wolf_pos": wolf_pos, "goat_pos": goat_pos, "cabbage_pos": cabbage_pos, "boat_pos": boat_pos}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

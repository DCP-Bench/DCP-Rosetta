# wolf_goat_cabbage: a cvc5 (Python) model from DCP Rosetta.
# Download the `wolf_goat_cabbage.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/wolf_goat_cabbage.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python wolf_goat_cabbage.py wolf_goat_cabbage.json

import cvc5.pythonic as c5


def create_model(instance):
    """A farmer with a wolf, a goat and a cabbage must cross a river by boat. The
    boat carries only the farmer and a single item. Left alone together, the wolf
    eats the goat and the goat eats the cabbage. Find a crossing in which nothing
    is eaten."""
    n_stages = instance["stage"]  # the number of stages, from the start (stage 0) to the end (the last stage)

    # The shore at each stage: true on the destination shore, false on the starting shore.
    boat = [c5.Bool(f"boat_{i}") for i in range(n_stages)]
    wolf = [c5.Bool(f"wolf_{i}") for i in range(n_stages)]
    goat = [c5.Bool(f"goat_{i}") for i in range(n_stages)]
    cabbage = [c5.Bool(f"cabbage_{i}") for i in range(n_stages)]

    solver = c5.Solver()

    # At the start everything is on the starting shore, and at the end everything is on the destination shore.
    solver.add(c5.Not(boat[0]), c5.Not(wolf[0]), c5.Not(goat[0]), c5.Not(cabbage[0]))
    solver.add(boat[n_stages - 1], wolf[n_stages - 1], goat[n_stages - 1], cabbage[n_stages - 1])

    # The farmer rows the boat across at every stage.
    solver.add([boat[i] != boat[i + 1] for i in range(n_stages - 1)])

    # The boat takes at most one item across. An item changes shore only when the boat takes it along.
    for i in range(n_stages - 1):
        # whether the wolf, the goat or the cabbage changes shore between stage i and stage i + 1
        wolf_moves = c5.Xor(wolf[i], wolf[i + 1])
        goat_moves = c5.Xor(goat[i], goat[i + 1])
        cabbage_moves = c5.Xor(cabbage[i], cabbage[i + 1])
        solver.add(
            c5.Implies(wolf_moves, wolf[i] == boat[i]),
            c5.Implies(goat_moves, goat[i] == boat[i]),
            c5.Implies(cabbage_moves, cabbage[i] == boat[i]),
            c5.Not(c5.And(wolf_moves, goat_moves)),
            c5.Not(c5.And(wolf_moves, cabbage_moves)),
            c5.Not(c5.And(goat_moves, cabbage_moves)),
        )

    # Whenever the wolf and the goat share a shore, the farmer is there too.
    # The same holds for the goat and the cabbage.
    for i in range(n_stages):
        solver.add(
            c5.Implies(wolf[i] == goat[i], boat[i] == goat[i]),
            c5.Implies(goat[i] == cabbage[i], boat[i] == goat[i]),
        )

    outputs = {
        "boat_pos": boat,
        "wolf_pos": wolf,
        "goat_pos": goat,
        "cabbage_pos": cabbage,
    }
    return solver, outputs


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

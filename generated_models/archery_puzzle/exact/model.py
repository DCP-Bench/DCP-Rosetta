# archery_puzzle: an Exact (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python archery_puzzle.py archery_puzzle.json

from exact import Exact


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values, and wants her total score as close as possible to a target score."""
    targets = instance["targets"]            # targets[i]: the points one hit on target i scores
    target_score = instance["target_score"]  # the total score she aims for

    solver = Exact()

    # Exact identifies its variables by name.
    # hits[i] is the number of arrows that hit target i. No target needs more
    # hits than the target score, since every target is worth at least 1 point.
    hits = [f"hits_{i}" for i in range(len(targets))]
    for name in hits:
        solver.addVariable(name, 0, target_score)

    # score is the total points scored, and deviation is how far it is from the target score.
    # A score above twice the target score is further away than no arrows at all, so the bound does not cut off the best answer.
    solver.addVariable("score", 0, 2 * target_score)
    solver.addVariable("deviation", 0, 2 * target_score)

    # The score is the points of all hits together.
    solver.addConstraint([(targets[i], hits[i]) for i in range(len(targets)) if targets[i]]
                         + [(-1, "score")], True, 0, True, 0)

    # overshoot is how far the score is above the target score, and undershoot is how far below.
    solver.addVariable("overshoot", 0, 2 * target_score)
    solver.addVariable("undershoot", 0, 2 * target_score)
    # The score is the target score plus the overshoot, minus the undershoot.
    solver.addConstraint([(1, "score"), (-1, "overshoot"), (1, "undershoot")],
                         True, target_score, True, target_score)
    # The deviation is the overshoot plus the undershoot. Minimizing it leaves at most one of the two nonzero.
    solver.addConstraint([(1, "overshoot"), (1, "undershoot"), (-1, "deviation")], True, 0, True, 0)

    # Get the score as close to the target score as possible.
    solver.setObjective([(1, "deviation")], minimize=True)

    return solver, {"hits": hits}


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

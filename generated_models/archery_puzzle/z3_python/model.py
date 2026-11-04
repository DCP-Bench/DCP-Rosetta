# archery_puzzle: a Z3 (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python archery_puzzle.py archery_puzzle.json

import z3


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values: she wants a total score as close as possible to a target score."""
    targets = instance["targets"]            # targets[i]: the score for one hit on target i
    target_score = instance["target_score"]  # the total score she aims for
    n = len(targets)                         # the number of targets

    # hits[i] is the number of arrows that hit target i
    hits = [z3.Int(f"hits_{i}") for i in range(n)]
    # score is the total points of all the arrows, deviation is how far that total is from the target score
    score = z3.Int("score")
    deviation = z3.Int("deviation")

    solver = z3.Optimize()
    # A target gets at least 0 hits, and at most as many as keep the total within twice the target
    # score. A hit is worth at least 1 point, so this is never more than target_score hits.
    for i in range(n):
        top = target_score
        if targets[i] > 0:
            top = min(top, 2 * target_score // targets[i])
        solver.add(hits[i] >= 0, hits[i] <= top)
    # The total and the deviation both stay between 0 and twice the target score.
    solver.add(score >= 0, score <= 2 * target_score)
    solver.add(deviation >= 0, deviation <= 2 * target_score)

    # The total is the points of all the hits together.
    solver.add(score == z3.Sum([hits[i] * targets[i] for i in range(n)]))
    # The deviation is at least the gap between the total and the target score, on either side.
    solver.add(deviation >= target_score - score, deviation >= score - target_score)

    # Come as close to the target score as possible.
    solver.minimize(deviation)

    return solver, {"hits": hits}


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

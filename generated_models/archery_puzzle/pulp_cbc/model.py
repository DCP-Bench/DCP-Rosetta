# archery_puzzle: a PuLP (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python archery_puzzle.py archery_puzzle.json

import pulp


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values: she wants a total score as close as possible to a target score."""
    targets = instance["targets"]            # targets[i]: the score for one hit on target i
    target_score = instance["target_score"]  # the total score she aims for
    n_targets = len(targets)                 # the number of targets

    problem = pulp.LpProblem("archery", pulp.LpMinimize)

    # hits[i] is the number of arrows that hit target i, at most target_score:
    # every target is worth at least one point, so more hits overshoot.
    hits = [pulp.LpVariable(f"hits_{i}", 0, target_score, cat="Integer")
            for i in range(n_targets)]
    # score is the total of all the points, which never needs to pass twice the target score.
    score = pulp.LpVariable("score", 0, 2 * target_score, cat="Integer")
    # deviation is the gap between the total score and the target score.
    deviation = pulp.LpVariable("deviation", 0, 2 * target_score, cat="Integer")

    # The total score is the sum of the points from all the hits.
    problem += score == pulp.lpSum(targets[i] * hits[i] for i in range(n_targets))

    # The deviation is never less than the gap, above or below the target score.
    problem += deviation >= target_score - score
    problem += deviation >= score - target_score

    # Land as close to the target score as possible.
    problem += deviation

    return problem, {"hits": hits}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

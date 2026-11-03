# archery_puzzle: a hermax (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install hermax`):
#   python archery_puzzle.py archery_puzzle.json

from hermax.model import Model


def create_model(instance):
    """An archer may shoot as many arrows as she likes at targets, each target
    worth a given number of points per hit. Choose how many arrows hit each target
    so that the total score is as close as possible to the target score."""
    targets = instance["targets"]      # targets[i]: points for a hit on target i
    goal = instance["target_score"]    # the total score the archer aims for
    n = len(targets)               # n: the number of targets

    m = Model()

    # hits[i] is the number of arrows that hit target i. Shooting nothing is already
    # `goal` points away from the goal, and any total above 2 * goal is further away
    # than that, so an optimal total stays within 2 * goal. Every target is worth at
    # least one point, so hits[i] is also at most `goal`: an optimal solution never
    # needs more arrows on one target than that. These two bounds only shrink the
    # domains; they do not exclude any optimal solution.
    hits = [m.int(f"hits_{i}", 0, min(goal, 2 * goal // targets[i])) for i in range(n)]

    # deviation is how far the total score is from the goal. It never needs to exceed
    # `goal`, since shooting nothing already gives that deviation.
    deviation = m.int("deviation", 0, goal)
    # total is the score of all arrows together: points per hit times the number of hits
    total = sum(targets[i] * hits[i] for i in range(n))

    # The deviation is at least the total's distance from the goal, in both directions:
    # deviation >= goal - total and deviation >= total - goal. Minimising the deviation
    # then pushes it down to exactly that distance.
    m &= (total + deviation >= goal)
    m &= (total - deviation <= goal)

    # Minimise how far the total score is from the target score.
    m.obj += deviation

    return m, {"hits": hits}


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

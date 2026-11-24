# archery_puzzle: a PyCSP3 model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python archery_puzzle.py archery_puzzle.json

from pycsp3 import *


def create_model(instance):
    """An archer may shoot any number of arrows at each of the targets, and her score is the
    sum of the values of her hits. Find the number of hits on each target that brings her
    score closest to the target score, minimising the absolute difference."""
    targets = instance["targets"]          # targets[k]: the points for one hit on target k
    target_score = instance["target_score"]  # the score the archer aims for
    n_targets = len(targets)

    # Any optimal score is below target_score + the largest ring value: if it exceeded the
    # target by at least one hit's value, removing that hit would get closer to the target.
    # The sum of the ring values is at least that largest value, so it bounds the score.
    max_score = target_score + sum(targets)

    # hits[k] is the number of arrows that land on target k
    hits = VarArray(size=n_targets, dom=range(max_score + 1))

    # The archer's total score, the sum of the values of all her hits
    score = Var(dom=range(max_score + 1))

    satisfy(
        # The score is the sum of the values of all hits.
        score == Sum(targets[k] * hits[k] for k in range(n_targets)),
    )

    # Minimise the absolute difference between the score and the target score.
    minimize(abs(score - target_score))

    return {"hits": hits}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

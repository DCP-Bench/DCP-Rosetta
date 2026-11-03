# archery_puzzle: a CPMpy model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python archery_puzzle.py archery_puzzle.json

import cpmpy as cp


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values: she wants a total score as close as possible to a target score."""
    targets = instance["targets"]            # targets[i]: the score for one hit on target i
    target_score = instance["target_score"]  # the total score she aims for

    # hits[i] is the number of arrows that hit target i; every target is worth at
    # least 1 point, so more than target_score hits on one target overshoots anyway
    hits = cp.intvar(0, target_score, shape=len(targets), name="hits")

    model = cp.Model()
    # Come as close as possible to the target score.
    model.minimize(cp.abs(target_score - cp.sum(hits * targets)))

    return model, {"hits": hits}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

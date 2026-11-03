# archery_puzzle: a Python-MIP (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python archery_puzzle.py archery_puzzle.json

import mip


def create_model(instance):
    """A young archer fires as many arrows as she likes at targets, each worth a set
    number of points per arrow. Find the number of arrows on each target so that the
    total score comes as close as possible to the target score."""
    targets = instance["targets"]            # targets[i] is the points for one arrow on target i
    target_score = instance["target_score"]  # the total score she aims for
    n_targets = len(targets)                 # the number of targets

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # hits[i] is the number of arrows on target i. Shooting nothing already misses the
    # target score by target_score, so an optimal total is at most twice the target
    # score, which caps the arrows on each target.
    hits = [
        model.add_var(f"hits_{i}", lb=0, ub=(2 * target_score) // targets[i], var_type=mip.INTEGER)
        for i in range(n_targets)
    ]

    # total is the score of all the arrows together.
    total = mip.xsum(targets[i] * hits[i] for i in range(n_targets))

    # deviation is how far the total score is from the target score.
    deviation = model.add_var("deviation", lb=0, ub=target_score, var_type=mip.INTEGER)
    # The deviation is at least the excess of the total over the target, and at least the shortfall.
    model += deviation >= total - target_score
    model += deviation >= target_score - total

    # Come as close to the target score as possible.
    model.objective = deviation

    return model, {"hits": hits}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

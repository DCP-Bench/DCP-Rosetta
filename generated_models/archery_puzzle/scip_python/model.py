# archery_puzzle: a SCIP (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python archery_puzzle.py archery_puzzle.json


from pyscipopt import Model, quicksum


def create_model(instance):
    """A young archer shoots arrows at a target with several rings, each ring
    worth a given number of points per arrow (targets), and she may shoot as
    many arrows as she likes. Choose how many arrows land on each ring so that
    the total score comes as close as possible to the target score. Report the
    number of hits on each ring (hits)."""
    target_score = instance["target_score"]  # the total score she is aiming for
    targets = instance["targets"]            # targets[j]: the points one arrow on ring j scores
    n = len(targets)                         # the number of rings

    # Bound on each hit count, from the data. In an optimal solution the total
    # score is below target_score + max(targets): if it were at least that much
    # over the target, taking away one arrow would bring it closer to the target.
    # So each ring j has at most (target_score + max(targets)) // targets[j] hits.
    top = target_score + max(targets)

    model = Model("archery_puzzle")

    # hits[j] is the number of arrows that land on ring j (a whole number, 0 or more)
    hits = [model.addVar(name=f"hits_{j}", vtype="I", lb=0, ub=top // targets[j])
            for j in range(n)]

    # score is the total points of all arrows: each ring's points times its hits
    score = quicksum(targets[j] * hits[j] for j in range(n))

    # gap is how far the total score is from the target score, in either direction
    # (never negative); the bound top covers any gap an optimal solution can have
    gap = model.addVar(name="gap", vtype="I", lb=0, ub=top)

    # The gap is at least the score above the target, and at least the score below it,
    # so at the optimum it equals the distance between score and target_score.
    model.addCons(gap >= score - target_score)  # the score is not above the target by more than the gap
    model.addCons(gap >= target_score - score)  # the score is not below the target by more than the gap

    # Objective: come as close to the target score as possible, i.e. minimise the gap.
    model.setObjective(gap, "minimize")

    return model, {"hits": hits}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

# archery_puzzle: a PySAT (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python archery_puzzle.py archery_puzzle.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """A young archer fires as many arrows as she pleases at targets of different
    values. She wants a total score as close as possible to the target score."""
    targets = instance["targets"]            # targets[i]: the points for one arrow on target i
    target_score = instance["target_score"]  # the total score she aims for
    n_targets = len(targets)                 # the number of targets

    pool = IDPool()  # gives each variable a number

    # hits[i] is the number of arrows that hit target i. A target worth t points takes
    # at most 2 * target_score // t arrows, so that the total stays within twice the
    # target score.
    hits = []
    for i, t in enumerate(targets):
        ub = target_score if t <= 0 else min(target_score, 2 * target_score // t)
        hits.append(Integer(f"hits_{i}", 0, ub, encoding="coupled", vpool=pool))

    # the total score, kept from 0 to twice the target score
    score = Integer("score", 0, 2 * target_score, encoding="order", vpool=pool)
    engine = IntegerEngine(vars=hits + [score], vpool=pool)

    # The total score is the points of all the arrows shot.
    engine.add_linear(sum(targets[i] * hits[i] for i in range(n_targets)) - score == 0)

    formula = WCNF()  # the constraints on the hits and the total, with the cost added below
    formula.extend(engine.clausify().clauses)

    # The distance from the target score is the cost. Each point the total goes over
    # the target score costs 1, and each point it falls short costs 1.
    for v in range(target_score + 1, 2 * target_score + 1):
        formula.append([-score.ge(v)], weight=1)
    for v in range(1, target_score + 1):
        formula.append([score.ge(v)], weight=1)

    # The objective in the problem's terms: the distance between the total score and the
    # target score, one per threshold the score passes above it or misses below it (as RC2's cost).
    objective = ([(1, score.ge(v)) for v in range(target_score + 1, 2 * target_score + 1)]
                 + [(1, -score.ge(v)) for v in range(1, target_score + 1)])

    return formula, {"hits": hits}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

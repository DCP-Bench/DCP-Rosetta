# archery_puzzle: a Paramita (Python) model from DCP Rosetta.
# Download the `archery_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/archery_puzzle.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python archery_puzzle.py archery_puzzle.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """A young archer fires as many arrows as she likes at targets worth different
    scores. She wants the total score as close as possible to the target score,
    above or below it."""
    target_score = instance["target_score"]  # the total score she aims for
    targets = instance["targets"]            # targets[i] is the score of one arrow on target i
    n_targets = len(targets)                 # the number of targets
    top_score = max(targets)                 # the score of one arrow on the best target

    # steps[k] is true when the count is at least k + 1. A count of at least k + 2
    # is also at least k + 1.
    def ordered(steps):
        return [If(steps[k + 1], steps[k]) for k in range(len(steps) - 1)]

    # at_least[i][k] is true when at least k + 1 arrows hit target i. A total of
    # target_score + top_score or more is never the best, since removing one arrow
    # would bring it closer to the target. So target i gets at most
    # (target_score + top_score - 1) // targets[i] arrows.
    at_least = []
    for i in range(n_targets):
        max_hits = (target_score + top_score - 1) // targets[i]
        at_least.append([Bool(f"hit_{i}_ge_{k + 1}") for k in range(max_hits)])
    # hits[i] is the number of arrows that hit target i
    hits = [sum(at_least[i]) for i in range(n_targets)]

    # The total score: every arrow on target i scores targets[i].
    total = sum(targets[i] * step for i in range(n_targets) for step in at_least[i])

    # overshoot[k] is true when the total is above the target score by at least k + 1.
    # The best total is above the target score by less than top_score.
    overshoot = [Bool(f"over_ge_{k + 1}") for k in range(top_score)]
    # undershoot[k] is true when the total is below the target score by at least k + 1.
    # The total is never below zero, so the undershoot is at most target_score.
    undershoot = [Bool(f"under_ge_{k + 1}") for k in range(target_score)]

    constraints = []  # the rules linking the hits, the total and the two steps
    # The steps of each count hold in order.
    for i in range(n_targets):
        constraints.extend(ordered(at_least[i]))
    constraints.extend(ordered(overshoot))
    constraints.extend(ordered(undershoot))
    # The overshoot is at least how far the total is above the target score.
    constraints.append(total - sum(overshoot) <= target_score)
    # The undershoot is at least how far the total is below the target score.
    constraints.append(total + sum(undershoot) >= target_score)

    # How far the total is from the target score, above or below.
    deviation = sum(overshoot) + sum(undershoot)

    # Minimise that distance.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-deviation, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"hits": hits}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = MaxSatSolver.from_name("EvalMaxSAT2022")
    # copy the formula into the solver: the hard clauses, then each soft clause with its weight
    solver.add_clauses(formula.hard_clauses())
    for weight, clause in formula.soft_clauses():
        solver.add_clause(clause, weight)

    if solver.solve() == MAXSAT_ANSWER.OPTIMAL:
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

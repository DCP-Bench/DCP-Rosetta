# twelve_pack: a Paramita (Python) model from DCP Rosetta.
# Download the `twelve_pack.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/twelve_pack.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python twelve_pack.py twelve_pack.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Given a target number of items, buy packs of different sizes so that the items
    meet or exceed the target, with as few items as possible."""
    packs = instance["packs"]    # packs[i]: the number of items in a pack of kind i
    target = instance["target"]  # the number of items needed

    # at_least[i][k] is true when at least k + 1 packs of kind i are bought. An optimal
    # purchase never buys more than ceil(target / p) packs of kind i, since one pack fewer
    # would still reach the target with fewer items.
    at_least = []
    for i, p in enumerate(packs):
        max_packs = -(-target // p)
        at_least.append([Bool(f"ge_{i}_{k}") for k in range(max_packs)])

    constraints = []

    # Buying k + 1 packs of a kind means buying k packs of that kind.
    for row in at_least:
        constraints += [If(row[k + 1], row[k]) for k in range(len(row) - 1)]

    # items_per_kind[i]: the number of items in the packs of kind i that are bought
    items_per_kind = [sum(p * b for b in row) for p, row in zip(packs, at_least)]
    # total: the number of items bought
    total = sum(items_per_kind)

    # The items bought meet or exceed the target.
    constraints.append(total >= target)

    # counts[i]: the number of packs of kind i that are bought
    counts = [sum(row) for row in at_least]

    # Minimise the items bought, so the purchase is as close to the target as the packs allow.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of items bought, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"counts": counts}, total


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import MAXSAT_ANSWER, MaxSatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs, objective = create_model(instances[index])

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
        print("objective =", evaluate(objective, truth))
    else:
        print("No solution")

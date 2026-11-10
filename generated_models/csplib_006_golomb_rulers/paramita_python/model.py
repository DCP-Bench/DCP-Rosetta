# csplib_006_golomb_rulers: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_006_golomb_rulers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_006_golomb_rulers.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_006_golomb_rulers.py csplib_006_golomb_rulers.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Iff, Or, add_to_weighted_container, to_cnf,
)


def smallest_prime_at_least(n):
    p = max(n, 2)
    while any(p % f == 0 for f in range(2, int(p ** 0.5) + 1)):
        p += 1
    return p


def erdos_turan_length(n_marks):
    # For a prime p at least n_marks, the marks 2pk + (k * k mod p), k = 0 to
    # n_marks - 1, form a Golomb ruler. An optimal ruler is no longer than this one.
    p = smallest_prime_at_least(n_marks)
    return max(2 * p * k + (k * k) % p for k in range(n_marks))


def create_model(instance):
    """Place marks on a ruler, the first at position 0, so that the distances between
    all pairs of marks are different. Find the shortest such Golomb ruler."""
    n_marks = instance["size"]  # the number of marks on the ruler
    last = erdos_turan_length(n_marks)  # the furthest position a mark can take

    # b[p] is true when a mark sits at position p
    b = [Bool(f"b_{p}") for p in range(last + 1)]

    constraints = []

    # The ruler starts at a mark at position 0 and has exactly n_marks marks.
    constraints.append(b[0])
    constraints.append(sum(b) == n_marks)

    # Each distance d is measured by at most one pair of marks.
    for d in range(1, last + 1):
        # q[p] is true when there are marks at both p and p + d
        q = [Bool(f"q_{p}_{d}") for p in range(last + 1 - d)]
        for p in range(last + 1 - d):
            constraints.append(If(b[p] & b[p + d], q[p]))
        constraints.append(sum(q) <= 1)

    # G[p][k] is true when at least k marks lie at positions before p.
    G = [[Bool(f"g_{p}_{k}") for k in range(n_marks + 1)] for p in range(last + 2)]
    # At least 0 marks: always true.
    for p in range(last + 2):
        constraints.append(G[p][0])
    # No position lies before 0, so no marks do.
    for k in range(1, n_marks + 1):
        constraints.append(~G[0][k])
    # At least k marks lie before p + 1 when they already lie before p, or when a
    # mark sits at p and at least k - 1 marks lie before p.
    for p in range(last + 1):
        for k in range(1, n_marks + 1):
            constraints.append(Iff(G[p + 1][k], Or([G[p][k], b[p] & G[p][k - 1]])))

    # The k-th mark is at the number of positions p where fewer than k marks lie at
    # or before p.
    marks = [(last + 1) + sum(-1 * G[p + 1][k] for p in range(last + 1)) for k in range(1, n_marks + 1)]
    # The length of the ruler is the position of its last mark.
    length = marks[-1]

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-length, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the length of the ruler, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"length": length, "marks": marks}, length


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

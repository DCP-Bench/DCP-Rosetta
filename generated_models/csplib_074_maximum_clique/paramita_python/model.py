# csplib_074_maximum_clique: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_074_maximum_clique.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_074_maximum_clique.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_074_maximum_clique.py csplib_074_maximum_clique.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """In a simple undirected graph, find a clique (a set of vertices that are all
    pairwise adjacent) of the largest possible size."""
    n = instance["n"]      # number of vertices
    adj = instance["adj"]  # adj[i][j] is 1 when vertices i and j are joined by an edge, else 0

    # c[i] is true when vertex i is in the clique
    c = [Bool(f"c_{i}") for i in range(n)]

    constraints = []

    # Two vertices that are not joined by an edge cannot both be in the clique.
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                constraints.append(~(c[i] & c[j]))

    # The clique is as large as possible: the number of its vertices.
    clique_size = sum(c)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(clique_size, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the size of the clique, maximised (the soft
    # clauses maximise it).
    return (formula, pool), {"c": c}, clique_size


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

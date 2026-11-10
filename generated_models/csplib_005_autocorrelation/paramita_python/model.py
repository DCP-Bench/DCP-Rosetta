# csplib_005_autocorrelation: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_005_autocorrelation.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_005_autocorrelation.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_005_autocorrelation.py csplib_005_autocorrelation.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, Iff, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """Choose a sequence of n values, each +1 or -1, whose periodic autocorrelations
    have the smallest possible sum of squares."""
    n = instance["n"]  # the length of the sequence

    # s[i] is true when the value at position i is +1, and false when it is -1
    s = [Bool(f"s_{i}") for i in range(n)]

    # The sequence value at position i is 2 * s[i] - 1.
    sequence = [2 * s[i] - 1 for i in range(n)]

    constraints = []
    energy = 0

    for k in range(1, n):
        # d[i] is true when positions i and (i + k) mod n hold different values
        d = [Bool(f"d_{k}_{i}") for i in range(n)]
        for i in range(n):
            j = (i + k) % n
            constraints.append(Iff(d[i], s[i] + s[j] == 1))

        # e[v] is true when exactly v of the pairs at shift k differ
        e = [Bool(f"e_{k}_{v}") for v in range(n + 1)]
        # Exactly one count v applies to shift k.
        constraints.append(sum(e) == 1)
        # The count of differing pairs at shift k is that v, so the autocorrelation
        # C_k = n - 2v. The energy adds C_k squared for each shift k.
        constraints.append(sum(d) == sum(v * e[v] for v in range(n + 1)))
        energy += sum((n - 2 * v) ** 2 * e[v] for v in range(n + 1))

    # Minimise the sum of the squared autocorrelations C_1 to C_(n-1).

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-energy, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the energy E, the sum of the squared
    # periodic autocorrelations, minimised (its negation is what the soft clauses
    # maximise).
    return (formula, pool), {"sequence": sequence}, energy


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

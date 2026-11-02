# covering_opl: a Paramita (Python) model from DCP Rosetta.
# Download the `covering_opl.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/covering_opl.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python covering_opl.py covering_opl.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, Or, add_to_weighted_container, to_cnf


def create_model(instance):
    """Select a set of workers to perform all the tasks while minimizing the cost.
    Each worker can perform certain tasks and has a hiring cost; every task has to be
    performed."""
    nb_workers = instance["nb_workers"]  # the number of workers
    cost = instance["Cost"]              # cost[i]: the hiring cost of worker i
    qualified = instance["Qualified"]    # qualified[t]: the workers who can perform task t, numbered from 1

    # hired[i] is true when worker i is hired
    hired = [Bool(f"hired_{i}") for i in range(nb_workers)]

    # Every task is performed by at least one hired worker who is qualified for it.
    constraints = [Or([hired[w - 1] for w in workers]) for workers in qualified]

    # The total hiring cost of the hired workers, which is minimised.
    total_cost = sum(cost[i] * hired[i] for i in range(nb_workers))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"total_cost": total_cost, "workers": hired}


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

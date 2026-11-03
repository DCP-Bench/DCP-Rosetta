# prod: a Paramita (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python prod.py prod.json

from math import lcm

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Choose a production quantity x[j] for each product j, between 0 and u[j], so that the
    time used, the sum of x[j] / a[j], stays at most b, and the total profit, the sum of
    c[j] * x[j], is as large as possible."""
    a = instance["a"]  # a[j]: one unit of product j uses 1 / a[j] of the time budget
    c = instance["c"]  # c[j]: the profit of one unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    b = instance["b"]  # the time budget
    products = range(len(a))

    # at_least[j][k] is true when x[j] is at least k + 1, for k = 0 .. u[j] - 1.
    # The true statements of product j count its quantity x[j].
    at_least = [[Bool(f"x_{j}_at_least_{k + 1}") for k in range(u[j])] for j in products]

    # Making at least k + 2 units of product j means making at least k + 1 units.
    cons = []
    for j in products:
        for k in range(u[j] - 1):
            cons.append(If(at_least[j][k + 1], at_least[j][k]))

    # x[j] is the number of units of product j made.
    x = [sum(at_least[j]) for j in products]

    # The time used stays within the budget. Both sides are multiplied by lcm(a), so that
    # every coefficient is a whole number.
    scale = lcm(*a)
    cons.append(sum((scale // a[j]) * bit for j in products for bit in at_least[j]) <= scale * b)

    # The total profit is the profit of every unit made.
    total_profit = sum(c[j] * bit for j in products for bit in at_least[j])

    # Maximise the total profit.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(total_profit, And(cons), to_cnf, formula, pool)

    return (formula, pool), {"x": x, "total_profit": total_profit}


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

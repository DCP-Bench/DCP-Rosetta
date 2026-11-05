# coins_grid: a Paramita (Python) model from DCP Rosetta.
# Download the `coins_grid.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/coins_grid.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python coins_grid.py coins_grid.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Place coins on an n by n grid, exactly c in every row and every column and at
    most one per cell, so that the sum of the squared horizontal distances of the coins
    from the main diagonal is as small as possible."""
    n = instance["n"]  # the grid has n rows and n columns
    c = instance["c"]  # the number of coins in each row and in each column

    # x[i][j] is true when cell (i, j) holds a coin
    x = [[Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    constraints = []  # the rules of the placement

    # Each row holds exactly c coins.
    constraints += [sum(x[i]) == c for i in range(n)]

    # Each column holds exactly c coins.
    constraints += [sum(x[i][j] for i in range(n)) == c for j in range(n)]

    # z: the sum of the squared horizontal distances of the coins from the main diagonal.
    # A coin in cell (i, j) is |i - j| cells from the diagonal, so it costs (i - j) ** 2.
    z = sum((i - j) ** 2 * x[i][j] for i in range(n) for j in range(n) if i != j)

    # keep the coins as close to the main diagonal as possible

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-z, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the sum of the quadratic distances from the
    # diagonal, minimised (its negation is what the soft clauses maximise).
    return (formula, pool), {"x": [[1 * x[i][j] for j in range(n)] for i in range(n)], "z": z}, z


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

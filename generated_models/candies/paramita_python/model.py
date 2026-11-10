# candies: a Paramita (Python) model from DCP Rosetta.
# Download the `candies.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/candies.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python candies.py candies.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Alice, a kindergarten teacher, gives candies to the children sitting in a line, each with a
    rating. Every child gets at least one candy, and of two neighbours the one with the higher
    rating gets more candies. Minimise the total number of candies."""
    ratings = instance["ratings"]  # ratings[i] is the rating of the child at position i
    n_children = len(ratings)      # the number of children in the line

    # In an optimal allocation no child needs more candies than there are children.
    max_candies = n_children

    # more[i][j] is true when the child at position i gets more than j + 1 candies
    more = [[Bool(f"more_{i}_{j}") for j in range(max_candies - 1)] for i in range(n_children)]

    constraints = []  # the rules of the allocation

    # A child with more than j + 1 candies also has more than j candies.
    for i in range(n_children):
        for j in range(1, max_candies - 1):
            constraints.append(If(more[i][j], more[i][j - 1]))

    # x[i] is the number of candies the child at position i gets: one, plus one for each
    # j where more[i][j] is true. So every child gets at least one candy.
    x = [1 + sum(more[i]) for i in range(n_children)]

    # Of two neighbours, the one with the higher rating gets more candies.
    for i in range(n_children - 1):
        if ratings[i] > ratings[i + 1]:
            constraints.append(x[i] >= x[i + 1] + 1)
        elif ratings[i] < ratings[i + 1]:
            constraints.append(x[i + 1] >= x[i] + 1)

    # z is the total number of candies. Alice wants to save money, so z is minimised.
    z = sum(x)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-z, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total number of candies, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"x": x, "z": z}, z


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

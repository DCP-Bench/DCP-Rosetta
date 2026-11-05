# cutting_stock: a Paramita (Python) model from DCP Rosetta.
# Download the `cutting_stock.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cutting_stock.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python cutting_stock.py cutting_stock.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Rolls of raw material are cut into rolls of several widths, following
    cutting patterns that each yield a given number of rolls of each width. Each
    width has a number of orders that must be met. Decide how many times each
    pattern is used so that the total number of raw rolls cut is as small as
    possible."""
    patterns = instance["num_rolls_width"]  # patterns[p][w]: rolls of width w that one raw roll gives with pattern p
    orders = instance["orders"]  # orders[w]: rolls of width w that must be cut
    n_patterns = instance["num_patterns"]  # the number of cutting patterns
    n_widths = len(orders)  # the number of widths

    # no pattern is used more often than the total number of orders
    max_uses = max(1, sum(orders))

    # at_least[p][i] is true when pattern p is used at least i + 1 times
    at_least = [[Bool(f"at_least_{p}_{i}") for i in range(max_uses)] for p in range(n_patterns)]
    constraints = []  # the rules the cutting plan must follow

    # Using a pattern at least i + 1 times means using it at least i times.
    for p in range(n_patterns):
        for i in range(max_uses - 1):
            constraints.append(If(at_least[p][i + 1], at_least[p][i]))

    # For each width, the rolls of that width cut with all patterns cover its orders.
    for w in range(n_widths):
        constraints.append(sum(patterns[p][w] * b for p in range(n_patterns) for b in at_least[p]) >= orders[w])

    # used[p] is the number of times pattern p is used
    used = [sum(at_least[p]) for p in range(n_patterns)]

    # the total number of raw rolls cut
    total = sum(used)

    # Cut as few raw rolls as possible.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the number of raw rolls cut, minimised (its
    # negation is what the soft clauses maximise).
    return (formula, pool), {"min_rolls_cut": total, "patterns_used": used}, total


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

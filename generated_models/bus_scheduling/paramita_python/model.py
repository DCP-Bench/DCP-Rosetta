# bus_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python bus_scheduling.py bus_scheduling.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """A day is cut into n_intervals successive 4-hour intervals, and each bus runs for 8
    successive hours, so it covers two intervals. The day wraps around. Find the fewest
    buses that meet the demand of every interval."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in interval i
    n_intervals = len(demands)     # the number of intervals in the day
    # No interval needs more buses starting in it than the largest demand.
    max_starts = max(demands)

    # at_least[i][k] is true when at least k + 1 buses start in interval i
    at_least = [[Bool(f"x_{i}_ge_{k + 1}") for k in range(max_starts)] for i in range(n_intervals)]
    # all constraints of the model
    cons = []

    # If at least k + 2 buses start in an interval, then at least k + 1 of them do.
    for i in range(n_intervals):
        for k in range(max_starts - 1):
            cons.append(If(at_least[i][k + 1], at_least[i][k]))

    # x[i] is the number of buses that start in interval i.
    x = [sum(at_least[i]) for i in range(n_intervals)]

    # The buses on duty in interval i are those that start in interval i and those that
    # start in the interval before it. prev is that earlier interval, wrapping around the day.
    for i in range(n_intervals):
        prev = (i - 1) % n_intervals
        cons.append(x[i] + x[prev] >= demands[i])

    # The total number of buses, to be minimised.
    total = sum(x)

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total, And(cons), to_cnf, formula, pool)

    return (formula, pool), {"x": x}


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

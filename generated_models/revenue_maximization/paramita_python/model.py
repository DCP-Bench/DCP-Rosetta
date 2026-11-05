# revenue_maximization: a Paramita (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python revenue_maximization.py revenue_maximization.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, add_to_weighted_container, to_cnf


def create_model(instance):
    """Flight packages are sold at a fixed price, each with an estimated demand. Choose how
    many units of each package to sell so that the total revenue is as large as possible,
    while the seats reserved on each flight leg stay within the seats available."""
    seats = instance["available_seats"]  # seats[l]: the passenger seats on flight leg l
    demand = instance["demand"]          # demand[p]: the estimated demand for package p
    revenue = instance["revenue"]        # revenue[p]: the price of one unit of package p
    delta = instance["delta"]            # delta[p][l]: 1 if package p uses flight leg l, 0 otherwise
    n_packages = len(demand)             # the number of packages
    n_legs = len(seats)                  # the number of flight legs

    constraints = []
    # units[p] is the number of units of package p to sell
    units = []
    for p in range(n_packages):
        # bits[k] is the k-th digit of that number, in binary; enough digits to reach the demand
        width = max(1, demand[p].bit_length())
        bits = [Bool(f"x_{p}_bit_{k}") for k in range(width)]
        units.append(sum((2 ** k) * bits[k] for k in range(width)))

    # No more units of a package are sold than its estimated demand.
    for p in range(n_packages):
        constraints.append(units[p] <= demand[p])

    # On each leg, the seats reserved by the packages sold do not exceed the seats available.
    for leg in range(n_legs):
        # reserved: seats on this leg taken by the units sold of each package that uses it
        reserved = [delta[p][leg] * units[p] for p in range(n_packages) if delta[p][leg]]
        if reserved:
            constraints.append(sum(reserved) <= seats[leg])

    # max_revenue is the total price of the packages sold
    total_revenue = sum(revenue[p] * units[p] for p in range(n_packages))

    # Make the revenue as large as possible.

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # maximise as soft clauses. The pool gives each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(total_revenue, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total revenue, maximised (the soft
    # clauses maximise it).
    return (formula, pool), {"packages_to_sell": units, "max_revenue": total_revenue}, total_revenue


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

# aircraft_assignment: a Paramita (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python aircraft_assignment.py aircraft_assignment.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = instance["availability"]  # availability[i]: aircraft available of type i
    demand = instance["demand"]              # demand[j]: passengers to carry on route j
    capabilities = instance["capabilities"]  # capabilities[i][j]: passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # costs[i][j]: cost of one aircraft of type i on route j
    n_types = len(availability)              # the number of aircraft types
    n_routes = len(demand)                   # the number of routes

    # at_least[i][j][k] is true when at least k + 1 aircraft of type i fly route j.
    # No route needs more aircraft of a type than the whole fleet, so the fleet size bounds the count.
    at_least = [
        [[Bool(f"at_least_{i}_{j}_{k}") for k in range(availability[i])] for j in range(n_routes)]
        for i in range(n_types)
    ]
    # allocation[i][j] is the number of aircraft of type i assigned to route j.
    allocation = [[sum(at_least[i][j]) for j in range(n_routes)] for i in range(n_types)]

    # The constraints of the assignment.
    constraints = []

    # A count of k + 1 or more aircraft on a route needs a count of k or more.
    for i in range(n_types):
        for j in range(n_routes):
            for k in range(availability[i] - 1):
                constraints.append(If(at_least[i][j][k + 1], at_least[i][j][k]))

    # A type has no more aircraft in use than it has available.
    for i in range(n_types):
        constraints.append(sum(allocation[i]) <= availability[i])

    # The aircraft on each route carry at least the route's demand.
    for j in range(n_routes):
        constraints.append(sum(capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= demand[j])

    # The total operating cost of the assigned aircraft, to minimise.
    total_cost = sum(costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes))

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"allocation": allocation}


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

# multi: a Paramita (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python multi.py multi.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """Multi-commodity transportation: ship every product from the origins to the
    destinations at the lowest total shipping cost, within the supplies, the demands
    and the lane limits."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units of all products together shipped from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins, n_destinations, n_products = len(supply), len(demand), len(supply[0])  # the numbers of origins, destinations and products

    # ship[i][j][p][k] is true when at least k+1 units of product p go from origin i to destination j
    ship = [[[[] for p in range(n_products)] for j in range(n_destinations)] for i in range(n_origins)]
    constraints = []  # the constraints of the transportation plan, collected below
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                # no more units than the tightest of the supply, the demand and the lane limit
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                ship[i][j][p] = [Bool(f"ship_{i}_{j}_{p}_ge_{k}") for k in range(1, ub + 1)]
                # If at least k+1 units go, then at least k units go.
                constraints += [If(ship[i][j][p][k], ship[i][j][p][k - 1]) for k in range(1, ub)]

    # Origin i ships out no more of product p than its supply.
    for i in range(n_origins):
        for p in range(n_products):
            # all shipments of product p out of origin i
            out = [b for j in range(n_destinations) for b in ship[i][j][p]]
            if out:
                constraints.append(sum(out) <= supply[i][p])

    # Destination j receives exactly its demand of each product.
    for j in range(n_destinations):
        for p in range(n_products):
            # all shipments of product p into destination j
            inc = [b for i in range(n_origins) for b in ship[i][j][p]]
            if inc:
                constraints.append(sum(inc) == demand[j][p])
            else:
                assert demand[j][p] == 0, "demand cannot be met: no shipment can reach it"

    # Units of all products together from origin i to destination j stay within the lane limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            # all units on the lane from origin i to destination j
            lane = [b for p in range(n_products) for b in ship[i][j][p]]
            if lane:
                constraints.append(sum(lane) <= limit[i][j])

    # cheapest[j][p]: the lowest shipping cost of one unit of product p to destination j
    cheapest = [[min(cost[i][j][p] for i in range(n_origins)) for p in range(n_products)]
                for j in range(n_destinations)]
    # Each unit delivered to destination j costs at least the cheapest rate for it, so this part of the cost is the same for every plan.
    total_cost = sum(cheapest[j][p] * demand[j][p]
                     for j in range(n_destinations) for p in range(n_products))
    # Each unit shipped pays its extra cost over the cheapest rate.
    total_cost += sum((cost[i][j][p] - cheapest[j][p]) * b
                      for i in range(n_origins) for j in range(n_destinations)
                      for p in range(n_products) for b in ship[i][j][p])

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(constraints), to_cnf, formula, pool)

    return (formula, pool), {"total_cost": total_cost}


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

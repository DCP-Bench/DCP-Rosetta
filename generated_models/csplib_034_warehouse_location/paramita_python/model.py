# csplib_034_warehouse_location: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from paramita.containers import WcnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_weighted_container, to_cnf


def create_model(instance):
    """A company decides which candidate warehouses to open and which open warehouse supplies each
    store. A warehouse can supply at most its capacity in stores, and each store is supplied by
    exactly one open warehouse. Minimise the maintenance cost of the open warehouses plus the
    supply cost of all stores."""
    n_warehouses = instance["n_suppliers"]     # the number of candidate warehouses
    n_stores = instance["n_stores"]            # the number of stores
    building_cost = instance["building_cost"]  # the maintenance cost of one open warehouse
    capacity = instance["capacity"]            # capacity[j]: the most stores warehouse j can supply
    cost = instance["cost_matrix"]             # cost[i][j]: the cost of supplying store i from warehouse j

    # open_warehouses[j] is true when warehouse j is open
    open_warehouses = [Bool(f"open_{j}") for j in range(n_warehouses)]
    # supplies[i][j] is true when warehouse j supplies store i
    supplies = [[Bool(f"supplies_{i}_{j}") for j in range(n_warehouses)] for i in range(n_stores)]

    # The constraints of the model, collected as they are added.
    constraints = []

    # Each store is supplied by exactly one warehouse.
    for i in range(n_stores):
        constraints.append(sum(supplies[i][j] for j in range(n_warehouses)) == 1)

    # A store is supplied only by a warehouse that is open.
    for i in range(n_stores):
        for j in range(n_warehouses):
            constraints.append(If(supplies[i][j], open_warehouses[j]))

    # A warehouse supplies no more stores than its capacity.
    for j in range(n_warehouses):
        constraints.append(sum(supplies[i][j] for i in range(n_stores)) <= capacity[j])

    # Maintenance cost of the open warehouses.
    maintenance = sum(building_cost * open_warehouses[j] for j in range(n_warehouses))
    # Supply cost of all stores.
    supply = sum(cost[i][j] * supplies[i][j] for i in range(n_stores) for j in range(n_warehouses))
    # The total cost, to minimise.
    total_cost = maintenance + supply

    # The warehouse that supplies each store.
    supplier_assignment = [sum(j * supplies[i][j] for j in range(n_warehouses))
                           for i in range(n_stores)]

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-total_cost, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total cost, minimised (its negation is
    # what the soft clauses maximise).
    return (formula, pool), {
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost,
    }, total_cost


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

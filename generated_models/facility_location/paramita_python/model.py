# facility_location: a Paramita (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then install Paramita with its EvalMaxSAT solver (the build needs Linux, git, cmake,
# a C++ compiler and zlib) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#maxsat-solvers/mse22-EvalMaxSAT2022'
#   python facility_location.py facility_location.json

from paramita.containers import WcnfFormula
from paramita.modelling import (
    And, Bool, DimacsVariablePool, If, Or, add_to_weighted_container, to_cnf,
)


def create_model(instance):
    """A company chooses which warehouses to open and how many units each open warehouse
    ships to each region, meeting every region's demand at the least total of fixed and
    shipping costs, under three rules about which warehouses are opened."""
    cities = instance["warehouse_s"]             # cities[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the fixed cost of opening warehouse i
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost of one unit from warehouse i to region j
    demands = instance["demands"]                # demands[j]: the number of units region j needs
    max_shipping = instance["max_shipping"]      # the most units one open warehouse can ship in total
    n_warehouses = len(cities)
    n_regions = len(demands)

    # The warehouse numbers of the three cities named in the rules.
    new_york = cities.index("New York")
    los_angeles = cities.index("Los Angeles")
    atlanta = cities.index("Atlanta")

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [Bool(f"open_{i}") for i in range(n_warehouses)]

    # route_cap[j] is the most units one warehouse can send to region j: its demand, or the
    # shipping limit when that is smaller.
    route_cap = [min(max_shipping, demands[j]) for j in range(n_regions)]

    # bits[i][j][k] is the digit for 2**k in the number of units shipped from warehouse i to region j.
    bits = [[[Bool(f"ship_{i}_{j}_b{k}") for k in range(max(1, route_cap[j].bit_length()))]
             for j in range(n_regions)] for i in range(n_warehouses)]

    # ships[i][j] is the number of units shipped from warehouse i to region j, read from its digits.
    ships = [[sum((1 << k) * b for k, b in enumerate(bits[i][j])) for j in range(n_regions)]
             for i in range(n_warehouses)]

    constraints = []

    # If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    constraints.append(If(open_warehouse[new_york], open_warehouse[los_angeles]))

    # No more than three warehouses can be operational.
    constraints.append(sum(open_warehouse) <= 3)

    # Either the Atlanta or the Los Angeles warehouse must be opened.
    constraints.append(Or([open_warehouse[atlanta], open_warehouse[los_angeles]]))

    # Each region receives exactly its demand from all warehouses together. No single
    # shipment exceeds the route_cap of its region.
    for j in range(n_regions):
        constraints.append(sum(ships[i][j] for i in range(n_warehouses)) == demands[j])
        for i in range(n_warehouses):
            constraints.append(ships[i][j] <= route_cap[j])

    # An open warehouse ships at most max_shipping units in total.
    for i in range(n_warehouses):
        constraints.append(sum(ships[i][j] for j in range(n_regions)) <= max_shipping * open_warehouse[i])

    # A closed warehouse ships nothing to any region.
    for i in range(n_warehouses):
        for j in range(n_regions):
            constraints.append(ships[i][j] <= route_cap[j] * open_warehouse[i])

    # The open warehouses together can carry the total demand.
    constraints.append(sum(max_shipping * open_warehouse[i] for i in range(n_warehouses)) >= sum(demands))

    # The fixed costs of the open warehouses.
    fixed_cost = sum(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))

    # cheapest[j] is the lowest cost per unit into region j.
    cheapest = [min(shipping_costs[i][j] for i in range(n_warehouses)) for j in range(n_regions)]

    # Each region receives exactly its demand, so its shipping cost splits into base, the
    # demands at the lowest prices, and extra, what is paid above the lowest price on each route.
    base = sum(demands[j] * cheapest[j] for j in range(n_regions))
    extra = sum((shipping_costs[i][j] - cheapest[j]) * ships[i][j]
                for i in range(n_warehouses) for j in range(n_regions))

    # The total cost is the fixed costs plus all shipping costs. The objective is the same
    # without the constant base.
    total_cost = fixed_cost + extra + base
    objective = fixed_cost + extra

    outputs = {
        "open_warehouse": open_warehouse,
        "ships": ships,
        "total_cost": total_cost,
    }

    # Encode into a weighted formula: the constraints as hard clauses, the value to
    # minimise as soft clauses, negated because MaxSAT maximises. The pool gives
    # each Bool its number in the clauses.
    formula = WcnfFormula()
    pool = DimacsVariablePool()
    add_to_weighted_container(-objective, And(constraints), to_cnf, formula, pool)

    # The objective in the problem's terms: the total cost, fixed plus shipping. The
    # soft clauses maximise the negation of the same cost without the constant base.
    return (formula, pool), outputs, total_cost


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

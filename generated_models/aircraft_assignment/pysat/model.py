# aircraft_assignment: a PySAT (Python) model from DCP Rosetta.
# Download the `aircraft_assignment.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/aircraft_assignment.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python aircraft_assignment.py aircraft_assignment.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Assign aircraft of several types to routes at minimal total operating cost.
    Each type has a limited number of aircraft, each route has a passenger demand
    to be met, and each type has a passenger capacity and cost on each route."""
    availability = instance["availability"]  # availability[a]: aircraft of type a that can be flown
    demand = instance["demand"]              # demand[r]: passengers to carry on route r
    capabilities = instance["capabilities"]  # capabilities[a][r]: passengers one aircraft of type a carries on route r
    costs = instance["costs"]                # costs[a][r]: operating cost of one aircraft of type a on route r
    n_types = len(availability)
    n_routes = len(demand)

    pool = IDPool()

    # allocation[a][r] is the number of aircraft of type a sent to route r. No route needs
    # more aircraft of a type than the whole fleet, so the fleet size is the upper bound
    # (at least 1, so every count has two values to choose from).
    allocation = [[Integer(f"allocation_{a}_{r}", 0, max(availability[a], 1), vpool=pool)
                   for r in range(n_routes)] for a in range(n_types)]

    # The rules on the counts.
    engine = IntegerEngine(vars=[x for row in allocation for x in row], vpool=pool)

    # The aircraft of each type over all routes do not exceed its availability.
    for a in range(n_types):
        engine.add_linear(sum(allocation[a][r] for r in range(n_routes)) <= availability[a])

    # The seats flown on each route cover its passenger demand.
    for r in range(n_routes):
        engine.add_linear(sum(capabilities[a][r] * allocation[a][r] for a in range(n_types)) >= demand[r])

    # The rules are hard, and the operating cost is added to them below.
    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Operating cost: k aircraft of type a on route r cost k * costs[a][r]. A negative cost
    # is charged as the shortfall from the largest count instead, which shifts the total
    # by a fixed amount.
    for a in range(n_types):
        for r in range(n_routes):
            count = allocation[a][r]
            unit_cost = costs[a][r]
            max_count = max(availability[a], 1)
            for k in range(0, max_count + 1):
                k_cost = unit_cost * k if unit_cost > 0 else -unit_cost * (max_count - k)
                if k_cost > 0:
                    formula.append([-count.equals(k)], weight=k_cost)

    # The objective in the problem's terms: the total operating cost (RC2's cost differs
    # from it by a fixed amount when some unit cost is negative).
    objective = [(costs[a][r], allocation[a][r]) for a in range(n_types) for r in range(n_routes)]

    return formula, {"allocation": allocation}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

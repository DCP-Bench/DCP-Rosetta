# revenue_maximization: a PuLP (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python revenue_maximization.py revenue_maximization.json

import pulp


def create_model(instance):
    """Sell units of fare packages, each package made of flight legs, so that the total revenue
    is as large as possible. No package sells more units than its estimated demand, and the
    seats reserved on each leg do not exceed the seats the leg has."""
    available_seats = instance["available_seats"]  # available_seats[l]: passenger seats on leg l
    demand = instance["demand"]                    # demand[p]: estimated demand for package p, in units
    revenue = instance["revenue"]                  # revenue[p]: price of one unit of package p
    delta = instance["delta"]                      # delta[p][l]: seats on leg l used by one unit of package p
    n_packages = len(demand)                       # number of packages
    n_legs = len(available_seats)                  # number of flight legs
    max_demand = max(demand)                       # no package sells more units than the largest demand

    problem = pulp.LpProblem("revenue", pulp.LpMaximize)

    # sell[p]: number of units of package p to sell
    sell = [pulp.LpVariable(f"sell{p}", 0, max_demand, cat="Integer")
            for p in range(n_packages)]

    # The seats reserved on each leg by the packages sold do not exceed the seats of that leg.
    for l in range(n_legs):
        problem += pulp.lpSum(delta[p][l] * sell[p] for p in range(n_packages)) <= available_seats[l]

    # Sell no more units of a package than its demand.
    for p in range(n_packages):
        problem += sell[p] <= demand[p]

    # max_revenue: total revenue of the packages sold. Its upper bound is the revenue if every
    # package sold its full demand.
    bound = sum(revenue[p] * demand[p] for p in range(n_packages))
    max_revenue = pulp.LpVariable("max_revenue", 0, bound, cat="Integer")
    problem += max_revenue == pulp.lpSum(revenue[p] * sell[p] for p in range(n_packages))

    # Maximise the revenue.
    problem += max_revenue

    return problem, {"packages_to_sell": sell, "max_revenue": max_revenue}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

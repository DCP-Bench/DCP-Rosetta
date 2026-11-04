# revenue_maximization: a Python-MIP (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python revenue_maximization.py revenue_maximization.json

import mip


def create_model(instance):
    """Flight legs have limited passenger seats, and packages of itineraries are sold
    at a given price with an estimated demand. Choose how many units of each package
    to sell so that the revenue is as large as possible, reserving seats for what is sold."""
    demand = instance["demand"]          # demand[p]: the estimated demand for package p
    revenue = instance["revenue"]        # revenue[p]: the price of one unit of package p
    seats = instance["available_seats"]  # seats[l]: the passenger seats on flight leg l
    delta = instance["delta"]            # delta[p][l]: 1 when package p uses flight leg l, 0 when not
    n_packages = len(demand)             # number of packages
    n_legs = len(seats)                  # number of flight legs

    model = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")

    # sell[p]: the number of units of package p to sell, at most its demand
    sell = [model.add_var(f"sell_{p}", lb=0, ub=demand[p], var_type=mip.INTEGER)
            for p in range(n_packages)]
    # max_revenue: the total revenue. Its upper bound is the revenue if every package sold its full demand.
    max_revenue = model.add_var("max_revenue", lb=0,
                                ub=sum(revenue[p] * demand[p] for p in range(n_packages)),
                                var_type=mip.INTEGER)

    # On each leg, the seats reserved for the units sold of the packages using it do not exceed the seats available.
    for leg in range(n_legs):
        model.add_constr(
            mip.xsum(sell[p] for p in range(n_packages) if delta[p][leg] == 1) <= seats[leg],
            f"seats_leg_{leg}",
        )

    # The total revenue is the price times the units sold, summed over the packages.
    model.add_constr(
        max_revenue == mip.xsum(revenue[p] * sell[p] for p in range(n_packages)),
        "total_revenue",
    )

    # Maximise the total revenue.
    model.objective = max_revenue

    return model, {"max_revenue": max_revenue, "packages_to_sell": sell}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

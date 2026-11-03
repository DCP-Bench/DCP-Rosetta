# revenue_maximization: a hermax (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install hermax`):
#   python revenue_maximization.py revenue_maximization.json

from hermax.model import Model


def create_model(instance):
    """Choose how many units of each flight package to sell so that the total revenue is
    as large as possible, without using more seats on any flight leg than it has."""
    demand = instance["demand"]              # demand[p]: the estimated number of units of package p
    revenue = instance["revenue"]            # revenue[p]: the price of one unit of package p
    delta = instance["delta"]                # delta[p][l] = 1 if package p uses flight leg l
    available_seats = instance["available_seats"]  # available_seats[l]: the seats on flight leg l
    n_packages = len(demand)                 # the number of packages
    n_legs = len(available_seats)            # the number of flight legs

    m = Model()
    # sell[p] is the number of units of package p to sell, from 0 up to its estimated demand
    sell = [m.int(f"sell_{p}", 0, demand[p]) for p in range(n_packages)]

    # Seat limits: every unit sold reserves one seat on each leg its package uses,
    # and a leg cannot carry more passengers than it has seats.
    for l in range(n_legs):
        users = [sell[p] for p in range(n_packages) if delta[p][l]]
        if users:  # a leg no package uses has no limit to post
            m &= (sum(users) <= available_seats[l])

    # The revenue collected from the units sold of every package.
    total_revenue = sum(revenue[p] * sell[p] for p in range(n_packages))

    # Maximise the total revenue: the objective is minimised, so minimise its negation.
    m.obj += -total_revenue

    return m, {"packages_to_sell": sell, "max_revenue": total_revenue}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

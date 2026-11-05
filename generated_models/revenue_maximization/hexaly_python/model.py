"""Revenue maximisation: sell flight packages within their demand and the seats on every leg, maximising revenue."""
import hexaly.optimizer as hx


def build(instance):
    # available_seats[l] = passenger seats on flight leg l; demand[p] = estimated demand for package p;
    # revenue[p] = price of one unit of package p; delta[p][l] = 1 if package p uses leg l, else 0
    seats, demand, revenue, delta = instance["available_seats"], instance["demand"], instance["revenue"], instance["delta"]
    # number of packages and of flight legs, read off the lengths of demand and available_seats
    packages, legs = len(demand), len(seats)
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # packages_to_sell[p] is the units of package p sold, at most its demand
    packages_to_sell = [model.int(0, demand[p]) for p in range(packages)]

    # We reserve seats according to the packages sold: the packages using a leg need at most its seats
    for l in range(legs):
        model.constraint(model.sum(delta[p][l] * packages_to_sell[p] for p in range(packages)) <= seats[l])

    # Maximise the revenue from the packages sold
    max_revenue = model.sum(revenue[p] * packages_to_sell[p] for p in range(packages))
    model.maximize(max_revenue)
    return optimizer, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}

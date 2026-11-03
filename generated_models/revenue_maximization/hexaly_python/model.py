"""Revenue maximisation: sell flight packages within their demand and the seats on every leg, maximising revenue."""
import hexaly.optimizer as hx


def build(instance):
    seats, demand, revenue, delta = instance["available_seats"], instance["demand"], instance["revenue"], instance["delta"]
    packages, legs = len(demand), len(seats)  # delta[p][l] = 1 if package p uses leg l
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # packages_to_sell[p] is the units of package p sold, at most its demand
    packages_to_sell = [model.int(0, demand[p]) for p in range(packages)]

    # The packages using a leg need at most its seats
    for l in range(legs):
        model.constraint(model.sum(delta[p][l] * packages_to_sell[p] for p in range(packages)) <= seats[l])

    # Maximise the revenue
    max_revenue = model.sum(revenue[p] * packages_to_sell[p] for p in range(packages))
    model.maximize(max_revenue)
    return optimizer, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}

from hermax.model import Model


def build(instance):
    demand = instance["demand"]
    revenue = instance["revenue"]
    delta = instance["delta"]                  # delta[p][l] = 1 if package p uses leg l
    available_seats = instance["available_seats"]
    n_packages = len(demand)
    n_legs = len(available_seats)

    m = Model()
    # sell[p] is the number of units of package p to sell, between 0 and its demand.
    sell = [m.int(f"sell_{p}", 0, demand[p]) for p in range(n_packages)]

    # Seats: the units sold reserve seats on every leg they use, and a leg
    # cannot carry more passengers than its seats.
    for l in range(n_legs):
        m &= (sum(sell[p] for p in range(n_packages) if delta[p][l]) <= available_seats[l])

    # Revenue collected from the packages sold.
    total_revenue = sum(revenue[p] * sell[p] for p in range(n_packages))

    # Maximise revenue: minimise its negation.
    m.obj += 0 - total_revenue

    return m, {"packages_to_sell": sell, "max_revenue": total_revenue}

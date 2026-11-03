# revenue_maximization: a PySAT (Python) model from DCP Rosetta.
# Download the `revenue_maximization.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/revenue_maximization.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python revenue_maximization.py revenue_maximization.json

from math import isqrt

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Flight legs have a limited number of seats, and each package of itineraries sells at a
    fixed price, with an estimated demand. Choose how many units of each package to sell so that
    the total revenue is as large as possible, without reserving more seats on a leg than it has."""
    available_seats = instance["available_seats"]  # available_seats[j]: passenger seats on flight leg j
    demand = instance["demand"]                    # demand[i]: the estimated demand for package i
    revenue = instance["revenue"]                  # revenue[i]: the price of one unit of package i
    delta = instance["delta"]                      # delta[i][j]: seats on leg j that one unit of package i uses
    n_packages = len(demand)  # the number of packages
    n_legs = len(available_seats)  # the number of flight legs
    packages = range(n_packages)

    # limit[i]: the most units of package i an optimal plan sells. That is its demand, cut to what
    # the seats of each leg it uses allow. A package that earns nothing per unit is never needed,
    # so its limit is 0.
    limit = []
    for i in packages:
        most = demand[i] if revenue[i] > 0 else 0
        for j in range(n_legs):
            if delta[i][j] > 0:
                most = min(most, available_seats[j] // delta[i][j])
        limit.append(max(most, 0))

    # Bounds on the best revenue. A greedy plan sells the packages highest revenue first, each as far
    # as the seats and demand allow. It is a feasible plan, so the best revenue is at least lower.
    # Selling every package up to its limit earns at least as much as any plan, so upper bounds the
    # best revenue from above.
    left = list(available_seats)  # left[j]: seats on leg j not yet taken by the greedy plan
    lower = 0
    for i in sorted(packages, key=lambda i: -revenue[i]):
        if limit[i] == 0:
            continue
        units = limit[i]
        for j in range(n_legs):
            if delta[i][j] > 0:
                units = min(units, left[j] // delta[i][j])
        for j in range(n_legs):
            left[j] -= delta[i][j] * units
        lower += revenue[i] * units
    upper = max(sum(revenue[i] * limit[i] for i in packages), lower + 1)

    # The largest demand bounds the units of each package. It is at least 1 so the range is never empty.
    top_units = max(max(demand), 1)

    # Every variable of the model comes from this pool.
    pool = IDPool()
    # packages_to_sell[i]: the units of package i sold, from 0 up to top_units
    packages_to_sell = [Integer(f"packages_to_sell{i}", 0, top_units, encoding="coupled", vpool=pool)
                        for i in packages]
    # max_revenue: the total revenue of the units sold, from lower to upper
    max_revenue = Integer("max_revenue", lower, upper, encoding="coupled", vpool=pool)
    # The whole-number variables above, which the constraints below are added to.
    engine = IntegerEngine(vars=packages_to_sell + [max_revenue], vpool=pool)

    # On each flight leg, the seats used by the units sold fit in the seats available.
    for j in range(n_legs):
        terms = [delta[i][j] * packages_to_sell[i] for i in packages if delta[i][j] != 0]
        if terms:
            engine.add_linear(sum(terms) <= available_seats[j])

    # No package sells more units than its demand.
    for i in packages:
        engine.add_linear(packages_to_sell[i] <= demand[i])

    # The model. Its whole-number variables take values in their ranges, and the constraints above hold.
    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Selling more units of a package than its limit is never part of an optimal plan.
    for i in packages:
        for u in range(limit[i] + 1, top_units + 1):
            formula.append([-packages_to_sell[i].equals(u)])

    # max_revenue is the revenue of the units sold, built up one package at a time: partial[s] is
    # true when the packages taken so far earn s. A partial revenue above upper, or too small to
    # reach lower with the packages still to come, cannot lead to an optimal plan and is dropped.
    # This keeps the model small, and once the sales are fixed the revenue is fixed too.

    # The packages, the largest possible revenue first.
    order = sorted(packages, key=lambda i: -revenue[i] * limit[i])
    # rest[k]: the most revenue the packages from position k in order can earn
    rest = [sum(revenue[i] * limit[i] for i in order[k:]) for k in range(n_packages + 1)]
    # No package taken yet, so the partial revenue is 0.
    start = pool.id(("partial", 0, 0))
    formula.append([start])
    # partial[s]: the packages taken so far earn s
    partial = {0: start}
    # Take the packages in order. Each number of units sold moves a partial revenue to a new one.
    for k, i in enumerate(order):
        # the partial revenues after package i
        nxt = {}
        for s, lit in partial.items():
            for u in range(limit[i] + 1):
                w = s + revenue[i] * u
                if w > upper or w + rest[k + 1] < lower:
                    # selling u here cannot lead to an optimal plan
                    formula.append([-lit, -packages_to_sell[i].equals(u)])
                    continue
                if w not in nxt:
                    nxt[w] = pool.id(("partial", k + 1, w))
                formula.append([-lit, -packages_to_sell[i].equals(u), nxt[w]])
        partial = nxt
    # max_revenue is the partial revenue once all packages are taken.
    for s, lit in partial.items():
        formula.append([-lit, max_revenue.equals(s)])
    # max_revenue cannot take a revenue that no plan earns.
    for v in range(lower, upper + 1):
        if v not in partial:
            formula.append([-max_revenue.equals(v)])

    # Revenue objective. Each level v above lower that max_revenue does not reach costs a penalty.
    # Lower levels cost more, so the cheapest plan has the highest revenue. The penalties are equal
    # over blocks of about the square root of the range, so the search settles a block at a time
    # rather than one level at a time.
    # span: the number of levels above lower
    span = upper - lower
    # group: the number of levels that share one penalty step
    group = isqrt(span) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([max_revenue.ge(v)], weight=1 + (upper - v) // group)

    return formula, {"packages_to_sell": packages_to_sell, "max_revenue": max_revenue}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

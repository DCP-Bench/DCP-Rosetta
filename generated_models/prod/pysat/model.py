# prod: a PySAT (Python) model from DCP Rosetta.
# Download the `prod.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/prod.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python prod.py prod.json

import math

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType, PBEnc


def create_model(instance):
    """Production planning: choose how many units of each product to make, within each product's
    limit, so that the capacity used stays within the capacity available and the total profit is
    as large as possible."""
    a = instance["a"]  # a[j]: the capacity used by one unit of product j is 1 / a[j]
    c = instance["c"]  # c[j]: the profit per unit of product j
    u = instance["u"]  # u[j]: the most units of product j that can be made
    b = instance["b"]  # the capacity available
    n_products = len(a)

    pool = IDPool()
    formula = WCNF()

    # The largest number of units of any product, and at least 1 so that the range is not a single value.
    top = max(max(u), 1)
    # x[j]: the number of units of product j made, a whole number from 0 to top
    x = [Integer(f"x_{j}", 0, top, encoding="coupled", vpool=pool) for j in range(n_products)]
    for var in x:
        formula.extend(var.domain_clauses())

    # No product is made beyond its limit u[j].
    for j in range(n_products):
        if u[j] < top:
            formula.append([-x[j].ge(max(u[j], 0) + 1)])

    # The least common multiple of the a[j], which turns the shares 1 / a[j] into whole numbers.
    lcm_a = math.lcm(*a)
    # One term for each unit of each product. A unit of product j uses lcm_a // a[j] of the capacity.
    lits, weights = [], []
    for j in range(n_products):
        for v in range(1, top + 1):
            lits.append(x[j].ge(v))
            weights.append(lcm_a // a[j])
    # The capacity used is at most b. Both sides are multiplied by lcm_a.
    formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=b * lcm_a,
                             vpool=pool).clauses)

    # The lowest and highest profit the limits allow.
    low = sum(min(0, c[j] * max(u[j], 0)) for j in range(n_products))
    high = sum(max(0, c[j] * max(u[j], 0)) for j in range(n_products))
    if high == low:
        high = low + 1
    # total_profit: the profit of the quantities made, sum of c[j] * x[j]
    total_profit = Integer("total_profit", low, high, encoding="coupled", vpool=pool)
    formula.extend(total_profit.domain_clauses())
    # Profit terms: one for each unit of each product, weighted by the profit per unit.
    profit_lits = [x[j].ge(v) for j in range(n_products) for v in range(1, top + 1)]
    profit_weights = [c[j] for j in range(n_products) for v in range(1, top + 1)]
    # Each step of total_profit above low.
    order = [total_profit.ge(k) for k in range(low + 1, high + 1)]
    # The profit terms minus the steps of total_profit above low sum to low. So total_profit
    # equals the profit of the units made.
    formula.extend(PBEnc.equals(lits=profit_lits + order,
                                weights=profit_weights + [-1] * len(order),
                                bound=low, vpool=pool,
                                encoding=EncType.bdd).clauses)

    # Maximise the profit. Each unit of a product with positive profit that is not made costs
    # its profit, and each unit of a product with negative profit that is made costs its loss.
    # Minimising these costs maximises the profit.
    for j in range(n_products):
        for v in range(1, top + 1):
            if c[j] > 0:
                formula.append([x[j].ge(v)], weight=c[j])
            elif c[j] < 0:
                formula.append([-x[j].ge(v)], weight=-c[j])

    # The objective in the problem's terms: the total profit (RC2's cost is the profit lost
    # against making every product at its limit).
    return formula, {"x": x, "total_profit": total_profit}, total_profit


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

# multi: a PySAT (Python) model from DCP Rosetta.
# Download the `multi.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/multi.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python multi.py multi.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Ship each product from the origins to the destinations, within every origin's supply and
    every lane's total limit, meeting every destination's demand, at the lowest total shipping cost."""
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p needed at destination j
    limit = instance["limit"]    # limit[i][j]: most units, over all products, shipped from origin i to destination j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of product p from origin i to destination j
    n_origins = len(supply)                # the number of origins
    n_destinations = len(demand)           # the number of destinations
    n_products = len(supply[0])            # the number of products
    max_supply = max(max(row) for row in supply)  # the largest supply of any product at any origin

    pool = IDPool()

    # x[i][j][p] is the number of units of product p shipped from origin i to destination j. It is at
    # most the smallest of the largest supply, the origin's supply of p and the lane limit, and at least 1.
    x = [[[Integer(f"x_{i}_{j}_{p}", 0, max(min(max_supply, supply[i][p], limit[i][j]), 1),
                   encoding="coupled", vpool=pool)
           for p in range(n_products)] for j in range(n_destinations)]
         for i in range(n_origins)]
    flat = [x[i][j][p] for i in range(n_origins) for j in range(n_destinations)
            for p in range(n_products)]  # all the shipments in one list
    engine = IntegerEngine(vars=flat, vpool=pool)

    formula = WCNF()
    # A yes/no fact that is always true. Its negation stands for a fact that is always false.
    true = pool.id("true")
    formula.append([true])
    false = -true

    # Sum and carry of three binary digits, each given as a yes/no fact.
    def full_adder(a, b, c):
        s, carry = pool.id(), pool.id()
        for va in (True, False):
            for vb in (True, False):
                for vc in (True, False):
                    odd = va ^ vb ^ vc
                    formula.append([-a if va else a, -b if vb else b,
                                    -c if vc else c, s if odd else -s])
        formula.extend([[-a, -b, carry], [-a, -c, carry], [-b, -c, carry],
                        [a, b, -carry], [a, c, -carry], [b, c, -carry]])
        return s, carry

    # Sum of two binary numbers, each a list of digits from the lowest digit up.
    def add(xs, ys):
        length = max(len(xs), len(ys))
        xs = xs + [false] * (length - len(xs))
        ys = ys + [false] * (length - len(ys))
        out, carry = [], false
        for a, b in zip(xs, ys):
            s, carry = full_adder(a, b, carry)
            out.append(s)
        return out + [carry]

    # An origin ships no more of a product than its supply.
    for i in range(n_origins):
        for p in range(n_products):
            engine.add_linear(sum(x[i][j][p] for j in range(n_destinations)) <= supply[i][p])

    # Shipping costs are never negative, so a surplus delivery never lowers the cost. Then each
    # destination receives exactly its demand. Otherwise it receives at least its demand.
    exact = all(c >= 0 for plane in cost for row in plane for c in row)
    for j in range(n_destinations):
        for p in range(n_products):
            delivered = sum(x[i][j][p] for i in range(n_origins))  # units of product p arriving at destination j
            if exact:
                engine.add_linear(delivered == demand[j][p])
            else:
                engine.add_linear(delivered >= demand[j][p])

    # The units of all products shipped on a lane stay within its limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            engine.add_linear(sum(x[i][j][p] for p in range(n_products)) <= limit[i][j])

    # Spell out the shipment rules above over yes/no facts.
    formula.extend(engine.clausify().clauses)

    # total is the shipping cost so far, in binary, one addition per shipment. A shipment of v units
    # on a lane costs cost * v, and its bit k is set exactly when v is one of the amounts whose cost
    # has bit k set.
    total = [false]
    upper = 0  # the most the whole plan could cost
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                var, c = x[i][j][p], cost[i][j][p]
                most = c * var.ub  # the most this shipment can cost
                upper += most
                term = []
                for k in range(max(most.bit_length(), 1)):
                    values = [var.equals(v) for v in range(var.lb, var.ub + 1) if ((c * v) >> k) & 1]
                    if not values:
                        term.append(false)
                        continue
                    bit = pool.id()  # bit k of this shipment's cost
                    formula.append([-bit] + values)
                    for lit in values:
                        formula.append([-lit, bit])
                    term.append(bit)
                total = add(total, term)

    # total_cost is a whole number from 0 to upper, the value the bits of the sum spell out.
    upper = max(upper, 1)
    width = upper.bit_length()
    # The plan costs at most upper, so the bits above its width are zero.
    for k in range(width, len(total)):
        formula.append([-total[k]])
    bits = (total + [false] * width)[:width]
    total_cost = Integer("total_cost", 0, upper, vpool=pool)
    for v in range(0, upper + 1):
        lit = total_cost.equals(v)
        spelled = [bits[k] if (v >> k) & 1 else -bits[k] for k in range(width)]
        for s in spelled:
            formula.append([-lit, s])
        formula.append([lit] + [-s for s in spelled])

    # Minimise the shipping cost. Every unit delivered to a destination costs at least the cheapest
    # origin's price for that product, and those units add up to a fixed sum. Only the extra over the
    # cheapest price is charged: each unit shipped from an origin pays its excess once.
    for j in range(n_destinations):
        for p in range(n_products):
            cheapest = min(cost[i][j][p] for i in range(n_origins)) if exact else 0
            for i in range(n_origins):
                c = cost[i][j][p] - cheapest
                if c > 0:
                    for v in range(1, x[i][j][p].ub + 1):
                        formula.append([-x[i][j][p].ge(v)], weight=c)

    # The objective in the problem's terms: the total shipping cost (RC2's cost is only the
    # excess over the cheapest origin, a fixed amount less).
    return formula, {"total_cost": total_cost}, total_cost


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

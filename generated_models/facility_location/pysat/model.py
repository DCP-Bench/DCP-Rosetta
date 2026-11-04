# facility_location: a PySAT (Python) model from DCP Rosetta.
# Download the `facility_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/facility_location.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python facility_location.py facility_location.json

from itertools import product
from math import isqrt

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc
from pysat.pb import EncType as PBType


def create_model(instance):
    """A company chooses which of four warehouses to open and how many units each
    ships to each region, meeting every region's demand at the least total of
    fixed and shipping costs, under three rules about which warehouses are opened."""
    names = instance["warehouse_s"]              # names[i]: the city of warehouse i
    fixed_costs = instance["fixed_costs"]        # fixed_costs[i]: the weekly fixed cost of warehouse i
    max_shipping = instance["max_shipping"]      # the most units one open warehouse can ship per week
    demands = instance["demands"]                # demands[j]: the weekly demand of region j
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: the cost per unit from warehouse i to region j
    n_warehouses = len(names)                    # the number of warehouses
    n_regions = len(demands)                     # the number of regions
    warehouses = range(n_warehouses)
    regions = range(n_regions)

    # The rules name three cities, so find their warehouses.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    # The largest number of units on one route, and at least 1 so that its range is never empty.
    ship_cap = max(max_shipping, 1)
    # The largest total cost the model allows.
    max_total = 10000

    def allowed(opened):
        """Whether a set of open warehouses obeys the three rules."""
        return ((not opened[new_york] or opened[los_angeles])
                and sum(opened) <= 3
                and (opened[atlanta] or opened[los_angeles]))

    # Upper bound on the total cost. Try every set of open warehouses that obeys the rules,
    # and ship each region's demand from the cheapest open warehouses that still have room.
    # Each such plan is feasible, so the cheapest of them bounds the optimum from above.
    upper = max_total
    for opened in product([False, True], repeat=n_warehouses):
        if not allowed(opened):
            continue
        # room[i]: the units warehouse i can still ship
        room = [max_shipping if opened[i] else 0 for i in warehouses]
        # cost: the fixed and shipping cost of this plan
        cost = sum(fixed_costs[i] for i in warehouses if opened[i])
        # need_left: the demand that no open warehouse can meet
        need_left = 0
        for j in sorted(regions, key=lambda j: -demands[j]):
            need = demands[j]
            for i in sorted(warehouses, key=lambda i: shipping_costs[i][j]):
                take = min(need, room[i])
                room[i] -= take
                need -= take
                cost += take * shipping_costs[i][j]
            need_left += need
        if need_left == 0:
            upper = min(upper, cost)

    # rank[j][k]: the warehouse with the k-th cheapest unit cost to region j
    rank = [sorted(warehouses, key=lambda i: shipping_costs[i][j]) for j in regions]
    # base: the shipping cost if each region were served entirely by its cheapest warehouse
    base = sum(shipping_costs[rank[j][0]][j] * demands[j] for j in regions)
    # Rule 3 opens at least one warehouse, so the total is at least the cheapest fixed cost on top of base.
    lower = base + min(fixed_costs)
    lower = max(0, min(lower, upper - 1))

    pool = IDPool()
    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [pool.id(("open", i)) for i in warehouses]
    # ships[i][j] is the number of units warehouse i sends to region j
    ships = [[Integer(f"ships_{i}_{j}", 0, ship_cap, encoding="coupled", vpool=pool)
              for j in regions] for i in warehouses]
    # total_cost is the whole cost of the plan, between lower and upper
    total_cost = Integer("total_cost", lower, max(upper, lower + 1), encoding="coupled",
                         vpool=pool)
    engine = IntegerEngine(vars=[s for row in ships for s in row] + [total_cost], vpool=pool)
    engine.add_linear(total_cost <= upper)

    # A warehouse ships at most max_shipping units per week in total.
    for i in warehouses:
        engine.add_linear(sum(ships[i]) <= max_shipping)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def neg(lit):
        """The opposite of a choice: its negation, or the flipped value of a constant."""
        return (not lit) if isinstance(lit, bool) else -lit

    def clause(*lits):
        """Require at least one of the choices to hold. A constant True satisfies it, a constant False is dropped."""
        if any(lit is True for lit in lits):
            return
        formula.append([lit for lit in lits if lit is not False])

    # units_from[j][k][v - 1] is true when region j gets at least v units from the warehouses ranked k and up.
    units_from = []

    def units_ge(j, k, v):
        """Whether region j gets at least v units from the warehouses ranked k and up."""
        if v <= 0:
            return True
        if v > demands[j] or k == n_warehouses:
            return False
        if k == 0:
            return True
        return units_from[j][k][v - 1]

    def ship_ge(j, k, v):
        """Whether the warehouse ranked k for region j sends at least v units to it."""
        if v <= 0:
            return True
        if v > demands[j] or v > ship_cap:
            return False
        return ships[rank[j][k]][j].ge(v)

    # A warehouse ships nothing unless it is open.
    for i in warehouses:
        for j in regions:
            formula.append([open_warehouse[i], ships[i][j].equals(0)])

    for j in regions:
        units_from.append({k: [pool.id(("units", j, k, v)) for v in range(1, demands[j] + 1)]
                           for k in range(1, n_warehouses)})

        # Getting at least v units from ranks k and up implies getting at least v - 1 of them.
        for k in range(1, n_warehouses):
            for v in range(1, demands[j]):
                formula.append([-units_from[j][k][v], units_from[j][k][v - 1]])

        # No warehouse sends region j more than its demand.
        for i in warehouses:
            if demands[j] + 1 <= ship_cap:
                formula.append([-ships[i][j].ge(demands[j] + 1)])

        # Units from ranks k and up are the units from the rank-k warehouse plus the units from
        # ranks k+1 and up, so each of the two sums below forces the other.
        for k in range(n_warehouses):
            # At least a from ranks k+1 and up, and at least b from rank k, make at least a + b from ranks k and up.
            for a in range(0, demands[j] + 1):
                for b in range(0, demands[j] + 2 - a):
                    if a + b > 0:
                        clause(neg(units_ge(j, k + 1, a)), neg(ship_ge(j, k, b)), units_ge(j, k, a + b))
            # At least v from ranks k and up needs at least a from ranks k+1 and up, or v - a from rank k.
            for v in range(1, demands[j] + 1):
                for a in range(0, v):
                    clause(neg(units_ge(j, k, v)), units_ge(j, k + 1, a + 1), ship_ge(j, k, v - a))

    # Rule 1: if New York is open, Los Angeles is open too.
    formula.append([-open_warehouse[new_york], open_warehouse[los_angeles]])

    # Rule 2: at most three warehouses are open.
    formula.extend(CardEnc.atmost(lits=open_warehouse, bound=3, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

    # Rule 3: Atlanta or Los Angeles is open, or both.
    formula.append([open_warehouse[atlanta], open_warehouse[los_angeles]])

    # The cost above base: the fixed cost of each open warehouse, and for each region and rank k >= 1
    # the extra unit cost of the rank-k warehouse over the rank k-1 one, times the units from ranks k and up.
    terms = []
    for i in warehouses:
        if fixed_costs[i] > 0:
            terms.append((open_warehouse[i], fixed_costs[i]))
    for j in regions:
        for k in range(1, n_warehouses):
            step = shipping_costs[rank[j][k]][j] - shipping_costs[rank[j][k - 1]][j]
            if step > 0:
                for v in range(1, demands[j] + 1):
                    terms.append((units_ge(j, k, v), step))

    # total_cost is base plus the cost terms. The bits hold total_cost minus lower in binary,
    # and the terms minus the bits add up to lower minus base.
    top = max(upper, lower + 1)
    # n_bits: the number of bits needed for the range of total_cost
    n_bits = max(top - lower, 1).bit_length()
    # bits[b]: bit b of total_cost minus lower
    bits = [pool.id(("cost bit", b)) for b in range(n_bits)]
    for v in range(lower, top + 1):
        for b in range(n_bits):
            formula.append([-total_cost.equals(v), bits[b] if ((v - lower) >> b) & 1 else -bits[b]])
    lits = [lit for lit, _ in terms] + bits
    weights = [w for _, w in terms] + [-(1 << b) for b in range(n_bits)]
    rhs = lower - base
    if rhs < 0:
        # The bound is written as a non-negative number: both sides flip sign.
        weights = [-w for w in weights]
        rhs = -rhs
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=rhs, vpool=pool,
                                encoding=PBType.adder).clauses)

    # Minimise total_cost. Each threshold v that total_cost reaches costs a weight, and the weight
    # rises by one for each group of about the square root of the range of thresholds, so the
    # total paid strictly rises with total_cost. Stratified RC2 then settles one group at a time.
    # group: the number of thresholds that share one weight
    group = isqrt(max(upper - lower, 1)) + 1
    for v in range(lower + 1, upper + 1):
        formula.append([-total_cost.ge(v)], weight=1 + (v - lower - 1) // group)

    return formula, {"total_cost": total_cost,
                     "open_warehouse": open_warehouse,
                     "ships": ships}


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
        # an Integer decodes its value from the model, a literal is true when it is in the model
        value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

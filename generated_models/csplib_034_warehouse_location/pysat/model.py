# csplib_034_warehouse_location: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_034_warehouse_location.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_034_warehouse_location.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_034_warehouse_location.py csplib_034_warehouse_location.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """A company decides which candidate warehouses to open and which open warehouse supplies each
    store. A warehouse can supply at most its capacity in stores, and each store is supplied by
    exactly one open warehouse. Minimise the maintenance cost of the open warehouses plus the
    supply cost of all stores."""
    n_warehouses = instance["n_suppliers"]     # the number of candidate warehouses
    n_stores = instance["n_stores"]            # the number of stores
    building_cost = instance["building_cost"]  # the maintenance cost of an open warehouse
    capacity = instance["capacity"]            # capacity[w]: the most stores warehouse w can supply
    cost = instance["cost_matrix"]             # cost[s][w]: the cost of supplying store s from warehouse w
    warehouses = range(n_warehouses)
    stores = range(n_stores)

    pool = IDPool()
    # supplier_assignment[s] is the warehouse that supplies store s
    supplier_assignment = [Integer(f"supplier_assignment_{s}", 0, n_warehouses - 1, vpool=pool)
                           for s in stores]
    # is_open[w] is true when warehouse w is open
    is_open = [pool.id(("open", w)) for w in warehouses]
    # total_cost is the maintenance cost plus the supply cost. Its lowest value has every store at
    # its cheapest warehouse and no warehouse open; its highest has every store at its dearest
    # warehouse and every warehouse open.
    low = sum(min(cost[s]) for s in stores)
    high = sum(max(cost[s]) for s in stores) + building_cost * n_warehouses
    total_cost = Integer("total_cost", low, high, encoding="coupled", vpool=pool)
    engine = IntegerEngine(vars=supplier_assignment + [total_cost], vpool=pool)
    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # serves(s, w) is true when store s is supplied by warehouse w
    def serves(s, w):
        return supplier_assignment[s].equals(w)

    # A warehouse supplies no more stores than its capacity.
    for w in warehouses:
        formula.extend(CardEnc.atmost(lits=[serves(s, w) for s in stores],
                                      bound=max(capacity[w], 0), vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # A warehouse is open exactly when it supplies at least one store.
    for w in warehouses:
        for s in stores:
            formula.append([-serves(s, w), is_open[w]])
        formula.append([-is_open[w]] + [serves(s, w) for s in stores])

    # total_cost is the supply cost of every store plus the maintenance cost of every open
    # warehouse. Each value of total_cost above its lowest one counts against that sum, so the
    # sum minus those counts equals the lowest value.
    lits, weights = [], []  # the cost terms: a store served by a warehouse, an open warehouse, and the counts
    for s in stores:
        for w in warehouses:
            lits.append(serves(s, w))
            weights.append(cost[s][w])
    for w in warehouses:
        lits.append(is_open[w])
        weights.append(building_cost)
    for v in range(low + 1, high + 1):
        lits.append(total_cost.ge(v))
        weights.append(-1)
    formula.extend(PBEnc.equals(lits=lits, weights=weights, bound=low, vpool=pool).clauses)

    # Minimise the total cost: serving store s from warehouse w costs cost[s][w], and an open
    # warehouse costs its maintenance.
    for s in stores:
        for w in warehouses:
            if cost[s][w] > 0:
                formula.append([-serves(s, w)], weight=cost[s][w])
    if building_cost > 0:
        for w in warehouses:
            formula.append([-is_open[w]], weight=building_cost)

    # The objective in the problem's terms: the maintenance plus supply cost (as RC2's cost).
    return formula, {"total_cost": total_cost, "open_warehouses": is_open,
                     "supplier_assignment": supplier_assignment}, total_cost


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
        # an Integer decodes its value from the model, a literal is true when it is in the model
        value = np.vectorize(lambda v: v.decode(model) if isinstance(v, Integer) else v in model)
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

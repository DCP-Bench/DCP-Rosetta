# netasgn: a PySAT (Python) model from DCP Rosetta.
# Download the `netasgn.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/netasgn.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python netasgn.py netasgn.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Project assignment: decide how many hours each person works on each project, so that
    every person works exactly their available hours and every project gets exactly the
    hours it requires, at the lowest total cost."""
    supply = instance["supply"]  # supply[i]: the hours person i has available
    demand = instance["demand"]  # demand[j]: the hours project j requires
    cost = instance["cost"]      # cost[i][j]: the cost per hour of person i working on project j
    limit = instance["limit"]    # limit[i][j]: the most hours person i can contribute to project j
    # Indices of the people, the projects, and every (person, project) pair.
    people = range(len(supply))
    projects = range(len(demand))
    cells = [(i, j) for i in people for j in projects]

    pool = IDPool()

    # A negative limit leaves no admissible number of hours.
    infeasible = any(limit[i][j] < 0 for i, j in cells)

    # assign[i][j] is the hours person i works on project j, from 0 up to the limit on the pair.
    assign = [[Integer(f"assign_{i}_{j}", 0, max(limit[i][j], 0),
                       encoding="coupled", vpool=pool)
               for j in projects] for i in people]

    # total_cost is the cost of all hours worked. Its lowest and highest possible values
    # come from the cheapest and dearest choice for each pair.
    low = sum(min(cost[i][j] * max(limit[i][j], 0), 0) for i, j in cells)
    high = sum(max(cost[i][j] * max(limit[i][j], 0), 0) for i, j in cells)
    total_cost = Integer("total_cost", low, high, vpool=pool)
    engine = IntegerEngine(vars=[assign[i][j] for i, j in cells] + [total_cost],
                           vpool=pool)

    # The hours each person works add up to their supply.
    for i in people:
        engine.add_linear(sum(assign[i][j] for j in projects) == supply[i])
    # The hours worked on each project add up to its demand.
    for j in projects:
        engine.add_linear(sum(assign[i][j] for i in people) == demand[j])

    # The constraints of the problem, and the cost to minimise.
    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    if infeasible:
        formula.append([])

    # Terms of the cost sum: each hour person i works on project j adds cost[i][j]. A negative
    # cost counts its magnitude on the hours not worked instead.
    lits, weights = [], []
    for i, j in cells:
        c = cost[i][j]
        for v in range(1, max(limit[i][j], 0) + 1):
            if c > 0:
                lits.append(assign[i][j].ge(v))
                weights.append(c)
            elif c < 0:
                lits.append(-assign[i][j].ge(v))
                weights.append(-c)
    # Number of binary digits needed for the range of total_cost above its lowest value.
    width = max(high - low, 0).bit_length()
    # bits[b] is binary digit b of total_cost above low.
    bits = [pool.id(("total_bit", b)) for b in range(width)]
    # total_cost equals the cost sum. The digits let the equation be a single weighted sum
    # over the terms and the digits, instead of one term for every value of total_cost.
    if lits or bits:
        formula.extend(PBEnc.equals(lits=lits + bits,
                                    weights=weights + [-(1 << b) for b in range(width)],
                                    bound=0, vpool=pool).clauses)
    # The digits of total_cost follow its value.
    for value in range(low, high + 1):
        for b in range(width):
            on = (value - low) >> b & 1
            formula.append([-total_cost.equals(value), bits[b] if on else -bits[b]])

    # Minimise total cost. Each hour person i works on project j costs cost[i][j]. A negative
    # cost pays its magnitude for every hour not worked, a constant shift.
    for i, j in cells:
        c = cost[i][j]
        for v in range(1, max(limit[i][j], 0) + 1):
            if c > 0:
                formula.append([-assign[i][j].ge(v)], weight=c)
            elif c < 0:
                formula.append([assign[i][j].ge(v)], weight=-c)

    # The objective in the problem's terms: the cost of all hours worked (RC2's cost differs
    # from it by a fixed amount when some cost is negative).
    return formula, {"assign": assign, "total_cost": total_cost}, total_cost


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

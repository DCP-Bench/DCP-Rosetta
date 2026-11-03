# csplib_013_progressive_party_problem: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def create_model(instance):
    """Timetable a party at a yacht club: some boats are hosts and the crews of the other
    boats visit host boats in successive periods, without exceeding any boat's capacity,
    revisiting a host or meeting another crew twice. Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # the number of boats
    n_periods = instance["n_periods"]  # the number of half-hour periods
    capacity = instance["capacity"]    # capacity[b]: the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b]: the number of people in the crew of boat b

    boats = range(n_boats)
    periods = range(n_periods)

    pool = IDPool()

    # is_host[b] is true when boat b is a host boat
    is_host = [pool.id(("is_host", b)) for b in boats]
    # visits[p][b] is the boat that the crew of boat b is on in period p
    visits = [[Integer(f"visits_{p}_{b}", 0, n_boats - 1, vpool=pool) for b in boats]
              for p in periods]
    engine = IntegerEngine(vars=[x for row in visits for x in row], vpool=pool)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def on(p, b, v):
        """The condition that the crew of boat b is on boat v in period p."""
        return visits[p][b].equals(v)

    # A host boat keeps its own crew on board in every period.
    for b in boats:
        for p in periods:
            formula.append([-is_host[b], on(p, b, b)])

    # A boat that is not a host is not visited, not even by its own crew.
    for v in boats:
        for p in periods:
            for b in boats:
                formula.append([is_host[v], -on(p, b, v)])

    # The people aboard a boat in a period, host crew and guest crews together, do not
    # exceed its capacity.
    for p in periods:
        for v in boats:
            formula.extend(PBEnc.leq(lits=[on(p, b, v) for b in boats],
                                     weights=crew_size, bound=capacity[v],
                                     vpool=pool).clauses)

    # A guest crew visits each host at most once.
    for b in boats:
        for v in boats:
            for p, q in combinations(periods, 2):
                formula.append([is_host[b], -on(p, b, v), -on(q, b, v)])

    # Two crews cannot be aboard the same boat in more than one period.
    for c1, c2 in combinations(boats, 2):
        # meet[p] holds if crews c1 and c2 are aboard the same boat in period p
        meet = [pool.id(("meet", p, c1, c2)) for p in periods]
        for p in periods:
            for v in boats:
                formula.append([-on(p, c1, v), -on(p, c2, v), meet[p]])
        formula.extend(CardEnc.atmost(lits=meet, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # The host boats together have room for all the people in all the crews.
    formula.extend(PBEnc.geq(lits=is_host, weights=capacity,
                             bound=sum(crew_size), vpool=pool).clauses)

    # Each host boat costs 1, so the cost is the number of host boats.
    for b in boats:
        formula.append([-is_host[b]], weight=1)

    return formula, {"visits": visits, "is_host": is_host}


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

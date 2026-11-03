# csplib_001_car_sequencing: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Car sequencing: order the cars on an assembly line so that, for each option, no
    window of consecutive cars holds more cars needing it than its station copes with."""
    at_most = instance["at_most"]      # at_most[o]: the most cars needing option o that its station copes with in a window
    per_slots = instance["per_slots"]  # per_slots[o]: the length of that window
    demand = instance["demand"]        # demand[t]: the number of cars of type t to build
    requires = instance["requires"]    # requires[t][o] is 1 when a car of type t needs option o

    n_types = len(demand)      # the number of car types
    n_options = len(at_most)   # the number of options
    n_cars = sum(demand)       # the number of cars, one slot on the line each

    pool = IDPool()
    # sequence[s] is the type of the car in slot s, with types numbered from 0
    sequence = [Integer(f"sequence{s}", 0, n_types - 1, vpool=pool) for s in range(n_cars)]
    engine = IntegerEngine(vars=sequence, vpool=pool)
    formula = engine.clausify()
    # is_type[s][t] is true when slot s holds a car of type t
    is_type = [[sequence[s].equals(t) for t in range(n_types)] for s in range(n_cars)]

    # Each car type fills as many slots as its demand.
    for t in range(n_types):
        formula.extend(CardEnc.equals(lits=[is_type[s][t] for s in range(n_cars)],
                                      bound=demand[t], vpool=pool,
                                      encoding=EncType.totalizer).clauses)

    for o in range(n_options):
        # the car types that need option o
        needing = [t for t in range(n_types) if requires[t][o]]
        # needs[s] is true when the car in slot s needs option o
        needs = []
        for s in range(n_cars):
            lit = pool.id(("needs", s, o))
            for t in needing:
                formula.append([-is_type[s][t], lit])
            formula.append([-lit] + [is_type[s][t] for t in needing])
            needs.append(lit)
        # The station for option o copes: in every window of per_slots[o] consecutive
        # slots, at most at_most[o] cars need it. A window no longer than at_most[o]
        # cannot overflow.
        for start in range(n_cars - per_slots[o] + 1):
            window = needs[start:start + per_slots[o]]  # the needs of the cars in this window
            if len(window) <= at_most[o]:
                continue
            formula.extend(CardEnc.atmost(lits=window, bound=at_most[o], vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # the car type in each slot, in the order of the line
    return formula, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

# csplib_001_car_sequencing: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

import z3


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    at_most = instance["at_most"]      # at_most[o]: the most cars in any window of per_slots[o] consecutive slots that may need option o
    per_slots = instance["per_slots"]  # per_slots[o]: the length of the window for option o
    demand = instance["demand"]        # demand[t]: the number of cars of type t to produce
    requires = instance["requires"]    # requires[t][o] is 1 when a car of type t needs option o

    n_cars = sum(demand)  # one slot on the line for each car
    n_types = len(demand)
    n_options = len(at_most)

    # sequence[s] is the type of the car in slot s (types are numbered from 0).
    sequence = [z3.Int(f"sequence_{s}") for s in range(n_cars)]

    # is_type[s][t] is true when the car in slot s is of type t.
    is_type = [[z3.Bool(f"is_type_{s}_{t}") for t in range(n_types)] for s in range(n_cars)]

    # needs[s][o] is true when the car in slot s needs option o.
    needs = [[z3.Bool(f"needs_{s}_{o}") for o in range(n_options)] for s in range(n_cars)]

    solver = z3.Solver()

    # The car in each slot has one type from 0 to n_types - 1, and is_type says which one.
    for s in range(n_cars):
        solver.add(sequence[s] >= 0, sequence[s] <= n_types - 1)
        solver.add([is_type[s][t] == (sequence[s] == t) for t in range(n_types)])
        solver.add(z3.PbEq([(is_type[s][t], 1) for t in range(n_types)], 1))

    # The car in each slot needs an option exactly when its type requires it.
    for s in range(n_cars):
        for o in range(n_options):
            requiring = [is_type[s][t] for t in range(n_types) if requires[t][o] == 1]
            solver.add(needs[s][o] == (z3.Or(requiring) if requiring else z3.BoolVal(False)))

    # The line holds as many cars of each type as demanded.
    for t in range(n_types):
        solver.add(z3.PbEq([(is_type[s][t], 1) for s in range(n_cars)], demand[t]))

    # Station capacity: in any window of per_slots[o] consecutive slots, at most at_most[o]
    # cars need option o.
    for o in range(n_options):
        for start in range(n_cars - per_slots[o] + 1):
            in_window = [(needs[s][o], 1) for s in range(start, start + per_slots[o])]
            solver.add(z3.PbLe(in_window, at_most[o]))

    # A consequence of the window rule that speeds up the search. Let total be the number of
    # cars that need option o, limit = at_most[o] and window = per_slots[o]. The last r slots
    # hold at most (r // window) * limit + min(limit, r % window) of them, so the first
    # n_cars - r slots must hold at least the rest. A line shorter than one window has no
    # window to check, so there is nothing to add.
    for o in range(n_options):
        total = sum(demand[t] for t in range(n_types) if requires[t][o] == 1)
        limit, window = at_most[o], per_slots[o]
        if n_cars < window:
            continue
        for r in range(1, n_cars):
            room_in_last = (r // window) * limit + min(limit, r % window)
            needed_before = total - room_in_last
            if needed_before > 0:
                solver.add(z3.PbGe([(needs[s][o], 1) for s in range(n_cars - r)], needed_before))

    return solver, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

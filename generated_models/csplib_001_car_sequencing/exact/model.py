# csplib_001_car_sequencing: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from exact import Exact


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    at_most = instance["at_most"]      # at_most[o]: the most cars needing option o in any window of per_slots[o] consecutive cars
    per_slots = instance["per_slots"]  # per_slots[o]: the length of the window for option o
    demand = instance["demand"]        # demand[t]: the number of cars of type t to produce
    requires = instance["requires"]    # requires[t][o] is 1 when a car of type t needs option o
    n_types = len(demand)              # the number of car types
    n_options = len(at_most)           # the number of options
    n_cars = sum(demand)              # one slot on the line for each car

    solver = Exact()

    # Exact identifies its variables by name.
    # is_type[s][t] is 1 when the car in slot s is of type t, and 0 when not.
    is_type = [[f"slot_{s}_is_type_{t}" for t in range(n_types)] for s in range(n_cars)]
    for s in range(n_cars):
        for t in range(n_types):
            solver.addVariable(is_type[s][t], 0, 1)

    # Each slot holds exactly one car type.
    for s in range(n_cars):
        solver.addConstraint([(1, is_type[s][t]) for t in range(n_types)], True, 1, True, 1)

    # sequence[s] is the type of the car in slot s, from 0 to n_types - 1.
    sequence = [f"sequence_{s}" for s in range(n_cars)]
    for s in range(n_cars):
        solver.addVariable(sequence[s], 0, n_types - 1)
        # The type of slot s is the type marked for it.
        solver.addConstraint([(t, is_type[s][t]) for t in range(1, n_types)] + [(-1, sequence[s])],
                             True, 0, True, 0)

    # The line holds as many cars of each type as demanded.
    for t in range(n_types):
        solver.addConstraint([(1, is_type[s][t]) for s in range(n_cars)], True, demand[t], True, demand[t])

    # Station capacity: in any window of per_slots[o] consecutive slots, at most at_most[o]
    # cars need option o.
    for o in range(n_options):
        # needing lists the car types that need option o.
        needing = [t for t in range(n_types) if requires[t][o]]
        if not needing:
            continue
        for start in range(n_cars - per_slots[o] + 1):
            # The slots of one window.
            window = range(start, start + per_slots[o])
            solver.addConstraint([(1, is_type[s][t]) for s in window for t in needing],
                                 False, 0, True, at_most[o])

    return solver, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

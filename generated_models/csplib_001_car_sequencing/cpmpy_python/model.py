# csplib_001_car_sequencing: a CPMpy model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

import cpmpy as cp
import numpy as np


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    at_most = instance["at_most"]    # at_most[o]: cars needing option o out of any per_slots[o] consecutive cars
    per_slots = instance["per_slots"]  # per_slots[o]: window length of the station for option o
    demand = instance["demand"]      # demand[t]: number of cars of type t to produce
    requires = np.array(instance["requires"])  # requires[t][o] is 1 when a car of type t needs option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)  # one slot on the line per car

    # sequence[s] is the type of the car in slot s of the line (types start from 0)
    sequence = cp.intvar(0, n_types - 1, shape=n_cars, name="sequence")

    # is_type[s, t] is true when the car in slot s has type t. The window sums below stay
    # linear over these booleans, which is cheaper than an element constraint per slot.
    is_type = cp.boolvar(shape=(n_cars, n_types), name="is_type")

    model = cp.Model()

    # Each slot's type variable agrees with its boolean indicators.
    for s in range(n_cars):
        for t in range(n_types):
            model.add(is_type[s, t] == (sequence[s] == t))

    # The line holds as many cars of each type as demanded.
    for t in range(n_types):
        model.add(cp.sum(is_type[:, t]) == demand[t])

    # Station capacity: in any window of per_slots[o] consecutive slots, at most
    # at_most[o] cars need option o. A line shorter than the window has no window to check.
    for o in range(n_options):
        needs_option = is_type * requires[:, o]  # needs_option[s, t]: slot s holds a type-t car that needs option o
        for start in range(n_cars - per_slots[o] + 1):
            model.add(cp.sum(needs_option[start:start + per_slots[o]]) <= at_most[o])

    return model, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

# csplib_001_car_sequencing: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Car sequencing: order the cars of an assembly line so that no option
    station has to handle more cars needing its option than it can cope with
    in any stretch of consecutive cars. Output the car type at each position
    of the line, with car types numbered from 0."""
    demand = np.array(instance["demand"])      # demand[c]: how many cars of type c are to be built
    requires = np.array(instance["requires"])  # requires[c][o] = 1 when a car of type c needs option o
    at_most = instance["at_most"]              # at_most[o]: the most cars needing option o allowed in one window
    per_slots = instance["per_slots"]          # per_slots[o]: the length of the window for option o

    num_types = len(demand)        # car types are numbered 0 .. num_types - 1
    num_cars = int(demand.sum())   # one position of the line per car

    model = Model("csplib_001_car_sequencing")

    # x[p, c] is 1 when position p of the line holds a car of type c, and 0 when not.
    # One-hot over car types: the type at a position is a choice among num_types, and the
    # options it needs are then a linear sum over requires, with no element constraint.
    x = model.addMatrixVar((num_cars, num_types), vtype="B", name="x")

    # Each position of the line holds exactly one car.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Each car type c appears exactly demand[c] times in the sequence.
    model.addMatrixCons(x.sum(axis=0) == demand)

    # load[p, o] is 1 when the car at position p needs option o: the one-hot row
    # of x picks out the matching row of requires.
    load = x @ requires

    # Option o's station copes with at most at_most[o] cars needing it in any
    # per_slots[o] consecutive positions. Every run of per_slots[o] consecutive
    # positions is a window; if the sequence is shorter than the window, the single
    # window is the whole sequence (the slice is cut at the end).
    for o in range(len(at_most)):
        window = per_slots[o]
        for start in range(max(num_cars - window, 0) + 1):
            model.addCons(load[start:start + window, o].sum() <= at_most[o])

    # Objective: none. Any sequence that meets the station limits is an answer.

    # The car type at position p is the one type number c for which x[p, c] is 1.
    sequence = x @ np.arange(num_types)

    return model, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

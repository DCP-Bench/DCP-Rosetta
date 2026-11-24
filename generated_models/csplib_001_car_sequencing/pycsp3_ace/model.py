# csplib_001_car_sequencing: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from pycsp3 import *


def create_model(instance):
    """A number of cars are to be produced, not all identical: they differ in the options
    they need. Each station of the assembly line installs one option and can handle at most
    a given number of the cars passing it in any window of consecutive cars. Arrange the cars
    in a sequence so that no station is overloaded."""
    demand = instance["demand"]        # demand[t] is the number of cars of type t to build
    requires = instance["requires"]    # requires[t][o] is 1 when cars of type t need option o
    at_most = instance["at_most"]      # at_most[o] is the most cars needing option o in any window of per_slots[o] cars
    per_slots = instance["per_slots"]  # per_slots[o] is the length of the window for option o
    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)               # the sequence holds every car to be built

    # sequence[p] is the type of the car in position p of the assembly line.
    sequence = VarArray(size=n_cars, dom=range(n_types))

    # needs[p][o] is 1 when the car in position p requires option o.
    needs = VarArray(size=[n_cars, n_options], dom={0, 1})

    # Each car type t occurs demand[t] times in the sequence.
    satisfy(Cardinality(sequence, occurrences={t: demand[t] for t in range(n_types)}))

    # The options of the car in each position follow from its type: the table gives the row requires[type].
    satisfy(
        Table(scope=[sequence[p]] + list(needs[p]), supports=[[t] + requires[t] for t in range(n_types)])
        for p in range(n_cars)
    )

    # Implied by the two constraints above: the cars needing option o are the cars of the types that require it.
    satisfy(
        Sum(needs[:, o]) == sum(demand[t] for t in range(n_types) if requires[t][o])
        for o in range(n_options)
    )

    # For each option, every window of per_slots[o] consecutive cars holds at most at_most[o] cars that need it.
    satisfy(
        Sum(needs[p:p + per_slots[o], o]) <= at_most[o]
        for o in range(n_options)
        for p in range(n_cars - per_slots[o] + 1)
    )

    return {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

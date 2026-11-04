# csplib_001_car_sequencing: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

import pulp


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    at_most = instance["at_most"]      # at_most[o]: the most cars that may need option o in any window of per_slots[o] consecutive cars
    per_slots = instance["per_slots"]  # per_slots[o]: the length of the window for option o
    demand = instance["demand"]        # demand[t]: the number of cars of type t to produce
    requires = instance["requires"]    # requires[t][o] is 1 when a car of type t needs option o

    n_types = len(demand)              # the number of car types
    n_options = len(at_most)           # the number of options
    n_cars = sum(demand)               # one position on the line for each car

    problem = pulp.LpProblem("car_sequencing", pulp.LpMinimize)

    # on_line[s][t] is 1 when the car in position s of the line is of type t.
    on_line = [[pulp.LpVariable(f"on_line_{s}_{t}", cat="Binary") for t in range(n_types)]
               for s in range(n_cars)]

    # sequence[s] is the type of the car in position s, counting types from 0.
    sequence = [pulp.LpVariable(f"sequence_{s}", 0, n_types - 1, cat="Integer")
                for s in range(n_cars)]

    # Each position holds exactly one car, and sequence gives its type.
    for s in range(n_cars):
        problem += pulp.lpSum(on_line[s]) == 1
        problem += sequence[s] == pulp.lpSum(t * on_line[s][t] for t in range(n_types))

    # The line holds as many cars of each type as demanded.
    for t in range(n_types):
        problem += pulp.lpSum(on_line[s][t] for s in range(n_cars)) == demand[t]

    # needs[s][o] is 1 when the car in position s needs option o.
    needs = [[pulp.LpVariable(f"needs_{s}_{o}", cat="Binary") for o in range(n_options)]
             for s in range(n_cars)]
    for s in range(n_cars):
        for o in range(n_options):
            problem += needs[s][o] == pulp.lpSum(requires[t][o] * on_line[s][t]
                                                 for t in range(n_types))

    # Station capacity: for each option o, in any window of per_slots[o] consecutive
    # positions, at most at_most[o] cars need it.
    for o in range(n_options):
        for s in range(n_cars - per_slots[o] + 1):
            problem += pulp.lpSum(needs[k][o] for k in range(s, s + per_slots[o])) <= at_most[o]

    return problem, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

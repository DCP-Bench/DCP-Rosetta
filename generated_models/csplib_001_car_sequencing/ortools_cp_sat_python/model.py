# csplib_001_car_sequencing: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    at_most = instance["at_most"]      # at_most[o]: the most cars in any window of per_slots[o] consecutive cars that may need option o
    per_slots = instance["per_slots"]  # per_slots[o]: the length of the window for option o
    demand = instance["demand"]        # demand[t]: the number of cars of type t to produce
    requires = instance["requires"]    # requires[t][o]: whether a car of type t needs option o

    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)  # one slot on the line for each car

    model = cp_model.CpModel()

    # is_type[s][t] is true when the car in slot s is of type t.
    is_type = [[model.new_bool_var(f"is_type_{s}_{t}") for t in range(n_types)]
               for s in range(n_cars)]

    # Every slot holds exactly one car type.
    for s in range(n_cars):
        model.add_exactly_one(is_type[s])

    # The line holds as many cars of each type as demanded.
    for t in range(n_types):
        model.add(sum(is_type[s][t] for s in range(n_cars)) == demand[t])

    # needs[s][o] is true when the car in slot s needs option o.
    needs = [[sum(is_type[s][t] for t in range(n_types) if requires[t][o])
              for o in range(n_options)]
             for s in range(n_cars)]

    # Station capacity: in any window of per_slots[o] consecutive slots, at most at_most[o]
    # cars need option o.
    for o in range(n_options):
        for start in range(n_cars - per_slots[o] + 1):
            model.add(sum(needs[s][o] for s in range(start, start + per_slots[o])) <= at_most[o])

    # sequence[s] is the type of the car in slot s.
    sequence = [sum(t * is_type[s][t] for t in range(n_types)) for s in range(n_cars)]
    return model, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

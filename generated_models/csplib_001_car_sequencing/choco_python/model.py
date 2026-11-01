# csplib_001_car_sequencing: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

from pychoco.model import Model


def create_model(instance):
    """Car sequencing: cars of different types, each needing some options, are put in
    a sequence on an assembly line. The station for an option can handle at most a
    given number of cars out of any given number of consecutive cars, so the cars
    needing an option must not bunch together."""
    at_most = instance["at_most"]      # at_most[o]: most cars needing option o in any window of per_slots[o] consecutive slots
    per_slots = instance["per_slots"]  # per_slots[o]: length of the window for the station of option o
    demand = instance["demand"]        # demand[t]: number of cars of type t to build
    requires = instance["requires"]    # requires[t][o] is 1 when a car of type t needs option o

    n_cars = sum(demand)          # one slot on the line for each car
    n_options = len(at_most)      # one station for each option
    n_types = len(demand)         # one car type for each entry of demand

    model = Model()

    # sequence[s] is the type of the car in slot s of the line.
    sequence = [model.intvar(0, n_types - 1, name=f"sequence_{s}") for s in range(n_cars)]
    # needs[s][o] is 1 when the car in slot s needs option o.
    needs = [[model.boolvar(name=f"needs_{s}_{o}") for o in range(n_options)]
             for s in range(n_cars)]

    # The line builds exactly the demanded number of cars of each type.
    for t in range(n_types):
        model.count(t, sequence, model.intvar(demand[t], demand[t])).post()

    # The options a slot needs are those of the car type in that slot.
    for s in range(n_cars):
        for o in range(n_options):
            model.element(needs[s][o], [requires[t][o] for t in range(n_types)], sequence[s]).post()

    # Station capacity: in any window of per_slots[o] consecutive slots, at most at_most[o]
    # cars need option o.
    for o in range(n_options):
        for s in range(n_cars - per_slots[o] + 1):
            model.sum([needs[k][o] for k in range(s, s + per_slots[o])], "<=", at_most[o]).post()

    return model, {"sequence": sequence}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

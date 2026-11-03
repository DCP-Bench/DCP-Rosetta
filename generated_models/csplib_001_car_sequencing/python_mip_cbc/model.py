# csplib_001_car_sequencing: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_001_car_sequencing.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_001_car_sequencing.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_001_car_sequencing.py csplib_001_car_sequencing.json

import mip


def create_model(instance):
    """Car sequencing: cars of several types are built on one assembly line, and each
    type needs some of the options. The station for an option can handle only a set
    number of cars in any run of consecutive cars, so the cars needing that option must
    not bunch together."""
    demand = instance["demand"]          # demand[t]: how many cars of type t to build
    requires = instance["requires"]      # requires[t][o]: 1 when a car of type t needs option o, 0 when not
    at_most = instance["at_most"]        # at_most[o]: most cars needing option o that the station handles in one run
    per_slots = instance["per_slots"]    # per_slots[o]: length of the run that the station for option o is checked over

    n_types = len(demand)
    n_cars = sum(demand)  # one position on the line for each car
    n_opts = len(at_most)

    model = mip.Model(solver_name="CBC")

    # x[p][t] is 1 when position p on the line holds a car of type t.
    x = [[model.add_var(f"x_{p}_{t}", var_type=mip.BINARY) for t in range(n_types)]
         for p in range(n_cars)]
    # sequence[p] is the type of the car at position p.
    sequence = [model.add_var(f"sequence_{p}", lb=0, ub=n_types - 1, var_type=mip.INTEGER)
                for p in range(n_cars)]

    # Each position holds exactly one car, and sequence[p] is that car's type.
    for p in range(n_cars):
        model += mip.xsum(x[p]) == 1
        model += sequence[p] == mip.xsum(t * x[p][t] for t in range(n_types))

    # Each car type appears on the line as many times as it is demanded.
    for t in range(n_types):
        model += mip.xsum(x[p][t] for p in range(n_cars)) == demand[t]

    # In every run of per_slots[o] consecutive positions, at most at_most[o] cars need option o.
    for o in range(n_opts):
        # The car types that need option o.
        needing = [t for t in range(n_types) if requires[t][o]]
        for start in range(n_cars - per_slots[o] + 1):
            model += mip.xsum(x[p][t] for p in range(start, start + per_slots[o]) for t in needing) <= at_most[o]

    return model, {"sequence": sequence}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

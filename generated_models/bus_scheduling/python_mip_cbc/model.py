# bus_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python bus_scheduling.py bus_scheduling.json

import mip


def create_model(instance):
    """Progress City needs enough buses on duty in each 4-hour interval to meet that
    interval's demand. Each bus works 8 successive hours, and the day wraps around, so the
    last interval is followed by the first. Find the fewest buses that do this."""
    demands = instance["demands"]  # demands[i] is the number of buses needed in interval i
    n_intervals = len(demands)     # the number of 4-hour intervals in the day

    model = mip.Model(solver_name="CBC")

    # x[i] is the number of buses that start their 8-hour shift in interval i. Such a bus is on
    # duty in interval i and in the interval after it. No optimal schedule starts more buses
    # in one interval than the largest demand.
    max_demand = max(demands)
    x = [model.add_var(f"x_{i}", lb=0, ub=max_demand, var_type=mip.INTEGER) for i in range(n_intervals)]

    # The buses on duty in interval i are those that start in interval i and those that
    # start in the interval before it. Interval 0 follows the last interval.
    for i in range(n_intervals):
        model += x[i - 1] + x[i] >= demands[i]

    # Minimise the total number of buses.
    model.objective = mip.xsum(x)

    return model, {"x": x}


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

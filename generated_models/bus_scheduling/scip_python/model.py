# bus_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python bus_scheduling.py bus_scheduling.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Progress City wants the fewest buses that cover the demand in each
    4-hour interval of the day. Each bus works 8 successive hours, which is
    two successive intervals, and the day wraps around: the last interval is
    followed by the first one."""
    demands = instance["demands"]  # demands[i]: buses needed in 4-hour interval i
    n = len(demands)               # the number of 4-hour intervals in the day

    model = Model("bus_scheduling")

    # x[i] is the number of buses that start their 8-hour shift at the beginning of
    # interval i. A bus starts at most once a day, so starting more buses than the
    # total demand is never needed: that sum is the upper bound, taken from the data.
    x = [model.addVar(f"x_{i}", vtype="I", lb=0, ub=sum(demands)) for i in range(n)]

    # Demand: in interval i, the buses that started in interval i and the buses that
    # started in the interval before it (wrapping around the day) must be enough.
    for i in range(n):
        model.addCons(x[i] + x[(i - 1) % n] >= demands[i])

    # Minimise the total number of buses scheduled over the day.
    model.setObjective(quicksum(x), "minimize")

    return model, {"x": x}


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

# bus_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python bus_scheduling.py bus_scheduling.json

import pulp


def create_model(instance):
    """The day is cut into equal time slots and each bus works two successive slots.
    Meet the bus demand of every slot with as few buses as possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    n_slots = len(demands)         # the number of time slots in the day

    problem = pulp.LpProblem("bus_scheduling", pulp.LpMinimize)

    # x[i] is the number of buses that start working in slot i. The total demand
    # bounds it, since no more buses than that are ever needed.
    x = [pulp.LpVariable(f"x_{i}", 0, sum(demands), cat="Integer") for i in range(n_slots)]

    # A bus works the slot it starts in and the next one, so the buses on duty in slot i
    # are those that started in slot i - 1 and those that started in slot i. The day wraps
    # around, so slot 0 is served by the buses that started in the last slot.
    for i in range(n_slots):
        problem += x[i - 1] + x[i] >= demands[i]

    # The number of buses is the number of buses that start, summed over all slots.
    problem += pulp.lpSum(x)

    return problem, {"x": x}


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

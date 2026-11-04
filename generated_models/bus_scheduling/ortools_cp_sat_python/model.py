# bus_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python bus_scheduling.py bus_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """The day is cut into equal time slots and each bus works two successive slots.
    Meet the bus demand of every slot with as few buses as possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    n_slots = len(demands)         # the number of time slots in the day

    model = cp_model.CpModel()

    # x[i] is the number of buses that start working in slot i. The total demand
    # bounds it, since no more buses than that are ever needed.
    x = [model.new_int_var(0, sum(demands), f"x_{i}") for i in range(n_slots)]

    # A bus works the slot it starts in and the next one, so the buses on duty in slot i
    # are those that started in slot i-1 and those that started in slot i. The day wraps
    # around, so slot 0 is served by the buses that started in the last slot.
    for i in range(n_slots):
        model.add(x[i - 1] + x[i] >= demands[i])

    # Use as few buses as possible.
    model.minimize(sum(x))

    return model, {"x": x}


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

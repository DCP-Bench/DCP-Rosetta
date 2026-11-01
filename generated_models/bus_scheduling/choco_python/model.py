# bus_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python bus_scheduling.py bus_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """The day is cut into equal time slots and each bus works two successive slots.
    Meet the bus demand of every slot with as few buses as possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    n_slots = len(demands)         # the number of time slots in the day

    model = Model()

    # x[i] is the number of buses that start working in slot i
    x = [model.intvar(0, sum(demands), name=f"x_{i}") for i in range(n_slots)]

    # A bus that starts in slot i also works slot i + 1, and the day wraps around, so slot
    # i + 1 is served by the buses that start in slot i and those that start in slot i + 1.
    for i in range(n_slots):
        nxt = (i + 1) % n_slots
        model.arithm(x[i], "+", x[nxt], ">=", demands[nxt]).post()

    # total_buses is the number of buses in use: all the buses started in the day.
    total_buses = model.intvar(0, sum(demands) * n_slots, name="total_buses")
    model.sum(x, "=", total_buses).post()

    # Use as few buses as possible.
    return model, {"x": x}, {"objective": total_buses, "maximize": False}


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

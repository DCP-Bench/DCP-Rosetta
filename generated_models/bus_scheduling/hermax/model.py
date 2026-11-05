# bus_scheduling: a hermax (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install hermax`):
#   python bus_scheduling.py bus_scheduling.json

from hermax.model import Model


def create_model(instance):
    """Progress City's bus schedule: the day is cut into equal 4-hour slots, and a bus
    works two consecutive slots (8 hours), the day wrapping around from the last slot
    to the first. Choose how many buses start in each slot so that every slot's demand
    is met with as few buses as possible."""
    demands = instance["demands"]  # demands[j]: buses needed in slot j
    n = len(demands)  # the number of 4-hour slots in the day

    m = Model()

    # x[i] is the number of buses that start working in slot i (their first of two slots).
    # A schedule never needs more buses starting in one slot than the largest demand:
    # any extra bus could be removed without breaking a slot's demand, so the largest
    # demand bounds every x[i] in an optimal schedule.
    x = m.int_vector("x", n, 0, max(demands))

    # Each slot j is served by the buses that start in slot j (still working) and by the
    # buses that started in the slot before it, wrapping around the day.
    for j in range(n):
        prev = (j - 1) % n
        m &= (x[j] + x[prev] >= demands[j])

    # Minimise the total number of buses, each counted once where it starts.
    total_buses = sum(x[i] for i in range(n))
    m.obj += total_buses

    # The objective in the problem's terms: the total number of buses, the cost minimised above.
    return m, {"x": x}, total_buses


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
        print("objective =", result[objective])
    else:
        print("No solution:", result.status)

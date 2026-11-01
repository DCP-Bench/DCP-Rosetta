# bus_scheduling: a CPMpy model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python bus_scheduling.py bus_scheduling.json

import cpmpy as cp


def create_model(instance):
    """The day is cut into equal time slots and each bus works two successive slots.
    Meet the bus demand of every slot with as few buses as possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    slots = len(demands)

    # x[i] is the number of buses that start working in slot i. The total demand
    # bounds it, since no more buses than that are ever needed.
    x = cp.intvar(0, sum(demands), shape=slots, name="x")

    model = cp.Model()
    # The buses available in a slot are those that start in it and those that started
    # in the slot before (the day wraps around, so slot -1 is the last slot), and they
    # must meet the demand of the slot.
    for i in range(slots):
        model.add(x[i - 1] + x[i] >= demands[i])

    # Use as few buses as possible.
    model.minimize(cp.sum(x))

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

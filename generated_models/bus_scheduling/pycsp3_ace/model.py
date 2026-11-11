# bus_scheduling: a PyCSP3 model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python bus_scheduling.py bus_scheduling.json

from pycsp3 import *


def create_model(instance):
    """Progress City needs a minimum number of buses over a cyclic day split into 4-hour slots.
    The demand is constant over each slot. Each bus operates 8 successive hours, so a bus that
    starts in a slot also works in the next one, and the first slot follows the last. The
    buses available in each slot, those starting in it and those that started in the slot
    before, must meet the demand of that slot. Find the minimum number of buses and how many
    of them start in each slot."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in 4-hour slot i
    n_slots = len(demands)         # the number of 4-hour slots in the cyclic day

    # x[i]: the number of buses that start in slot i. No slot needs more starting buses than the
    # whole day's total demand: starting demands[i] buses in every slot already covers every
    # slot with sum(demands) buses, so an optimal schedule never has x[i] above sum(demands).
    x = VarArray(size=n_slots, dom=range(sum(demands) + 1))

    satisfy(
        # Slot i is served by the buses starting in slot i and those starting in the slot before.
        # The day is cyclic, so the slot before slot 0 is the last slot.
        [x[i] + x[(i - 1) % n_slots] >= demands[i] for i in range(n_slots)]
    )

    # The number of buses is the total number of buses that start during the day: minimise it.
    minimize(Sum(x))

    return {"x": x}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is OPTIMUM:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

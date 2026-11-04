# bus_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python bus_scheduling.py bus_scheduling.json

import z3


def create_model(instance):
    """The day is cut into equal time slots and each bus works two successive slots.
    Meet the bus demand of every slot with as few buses as possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    slots = len(demands)

    # x[i] is the number of buses that start working in slot i. The total demand
    # bounds it, since no more buses than that are ever needed.
    x = [z3.Int(f"x_{i}") for i in range(slots)]
    solver = z3.Optimize()

    solver.add([z3.And(x_i >= 0, x_i <= sum(demands)) for x_i in x])

    # The buses working in a slot are those that start in it and those that started in
    # the slot before. The day wraps around, so the slot before the first is the last.
    solver.add([x[i - 1] + x[i] >= demands[i] for i in range(slots)])

    # Use as few buses as possible.
    solver.minimize(z3.Sum(x))

    return solver, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

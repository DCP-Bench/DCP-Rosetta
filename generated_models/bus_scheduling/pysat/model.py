# bus_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `bus_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/bus_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python bus_scheduling.py bus_scheduling.json

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """The day is cut into equal time slots and each bus works two successive slots.
    Meet the bus demand of every slot with as few buses as possible."""
    demands = instance["demands"]  # demands[i]: the number of buses needed in slot i
    slots = len(demands)           # the number of time slots in the day

    pool = IDPool()
    # The most buses that start in one slot. A slot never needs more starting buses than the
    # largest demand, since any excess could be dropped from the schedule.
    top = max(max(demands), 1)
    # x[i] is the number of buses that start work in slot i
    x = [Integer(f"x_{i}", 0, top, vpool=pool) for i in range(slots)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # A bus starting in slot i works slot i and the next slot, so the buses at work in slot i+1
    # are those starting in slot i and in slot i+1. The day wraps around, so the last slot is
    # followed by the first.
    for i in range(slots):
        engine.add_linear(x[i] + x[(i + 1) % slots] >= demands[(i + 1) % slots])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Each bus costs one. A slot that starts v buses costs v, so the total cost is the total
    # number of buses.
    for i in range(slots):
        for v in range(1, top + 1):
            formula.append([-x[i].equals(v)], weight=v)

    # The objective in the problem's terms: the total number of buses (as RC2's cost).
    objective = [(1, xi) for xi in x]

    return formula, {"x": x}, objective


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs, objective = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

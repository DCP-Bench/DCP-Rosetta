# csplib_022_bus_driver_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_022_bus_driver_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_022_bus_driver_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_022_bus_driver_scheduling.py csplib_022_bus_driver_scheduling.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF


def create_model(instance):
    """Choose bus driver shifts so that every piece of work is covered by exactly one chosen
    shift, using as few shifts as possible. Each possible shift covers some of the pieces."""
    n_work = instance["num_work"]  # the number of pieces of work, numbered from 0
    shifts = instance["shifts"]    # shifts[i]: the pieces of work that possible shift i covers
    n_shifts = len(shifts)

    pool = IDPool()
    formula = WCNF()

    # x[i] is true when shift i is chosen.
    x = [pool.id(("x", i)) for i in range(n_shifts)]

    # The chosen shifts cover each piece of work exactly once.
    for t in range(n_work):
        covering = [x[i] for i in range(n_shifts) if t in shifts[i]]  # the shifts that cover piece t
        if not covering:
            # No shift covers this piece, so no choice of shifts is valid.
            formula.append([x[0]])
            formula.append([-x[0]])
            continue
        formula.extend(CardEnc.equals(lits=covering, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Each chosen shift costs one, so the objective is the number of shifts chosen.
    for i in range(n_shifts):
        formula.append([-x[i]], weight=1)

    # The objective in the problem's terms: the number of shifts chosen (as RC2's cost).
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
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

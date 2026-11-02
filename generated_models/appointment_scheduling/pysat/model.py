# appointment_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool


def create_model(instance):
    """Schedule each person into one interview slot in which they are free, with
    one person in each slot."""
    free = instance["m"]  # free[i][j] is 1 when person i is free in slot j
    n_people = len(free)  # the number of people, which is also the number of slots

    pool = IDPool()  # gives each variable a number

    # x[i][j] is true when person i is interviewed in slot j
    x = [[pool.id(("x", i, j)) for j in range(n_people)] for i in range(n_people)]

    formula = CNF()  # the constraints on the schedule

    # A person is never placed in a slot where they are busy.
    for i in range(n_people):
        for j in range(n_people):
            if not free[i][j]:
                formula.append([-x[i][j]])

    # Each person gets exactly one slot.
    for i in range(n_people):
        formula.extend(CardEnc.equals(lits=x[i], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Each slot gets exactly one person.
    for j in range(n_people):
        column = [x[i][j] for i in range(n_people)]  # every person's variable for slot j
        formula.extend(CardEnc.equals(lits=column, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    return formula, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

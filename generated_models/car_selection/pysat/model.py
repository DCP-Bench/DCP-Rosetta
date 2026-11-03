# car_selection: a PySAT (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python car_selection.py car_selection.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF


def create_model(instance):
    """Assign participants to cars to maximise the number of assignments. Each participant is
    interested in some of the cars and gets at most one of them, and each car goes to at most one
    participant."""
    possible = instance["possible_assignments"]  # possible[i][j] is 1 when participant i is interested in car j
    n_participants = len(possible)               # the number of participants
    n_cars = len(possible[0])                    # the number of cars

    pool = IDPool()

    # assignments[i][j] is true when participant i gets car j
    assignments = [[pool.id(("assign", i, j)) for j in range(n_cars)]
                   for i in range(n_participants)]

    formula = WCNF()

    # A participant gets only a car they are interested in.
    for i in range(n_participants):
        for j in range(n_cars):
            if not possible[i][j]:
                formula.append([-assignments[i][j]])

    # Each participant gets at most one car.
    for i in range(n_participants):
        formula.extend(CardEnc.atmost(lits=assignments[i], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Each car goes to at most one participant. column holds the assignments of car j.
    for j in range(n_cars):
        column = [assignments[i][j] for i in range(n_participants)]
        formula.extend(CardEnc.atmost(lits=column, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Maximise the number of assignments. Each interested pair left unassigned costs 1, so the cost
    # is the number of interested pairs not assigned.
    for i in range(n_participants):
        for j in range(n_cars):
            if possible[i][j]:
                formula.append([assignments[i][j]], weight=1)

    return formula, {"assignments": assignments}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.examples.rc2 import RC2Stratified

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    # falsify as little soft-clause weight as possible
    model = RC2Stratified(formula).compute()

    if model:
        # a literal is true when it is in the model
        value = np.vectorize(lambda lit: lit in model)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

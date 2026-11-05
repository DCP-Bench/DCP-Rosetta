# assignment_costs: a PySAT (Python) model from DCP Rosetta.
# Download the `assignment_costs.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/assignment_costs.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python assignment_costs.py assignment_costs.json

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.pb import PBEnc


def create_model(instance):
    """Assign each task to exactly one person, with each person taking at most one
    task, so that the total cost is as small as possible. Not every person needs
    a task."""
    cost = instance["cost"]    # cost[i][j] is the cost of person j doing task i
    n_tasks = len(cost)        # the number of tasks
    n_people = len(cost[0])    # the number of people

    pool = IDPool()  # gives each variable a number

    # x[i][j] is true when task i is assigned to person j
    x = [[pool.id(("x", i, j)) for j in range(n_people)] for i in range(n_tasks)]

    formula = WCNF()  # the constraints, with the cost added below

    # Each task is assigned to exactly one person.
    for i in range(n_tasks):
        formula.extend(CardEnc.equals(lits=x[i], bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Each person takes at most one task.
    for j in range(n_people):
        column = [x[i][j] for i in range(n_tasks)]  # every task's variable for person j
        formula.extend(CardEnc.atmost(lits=column, bound=1, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    lits = [x[i][j] for i in range(n_tasks) for j in range(n_people)]  # every task-person pair
    weights = [cost[i][j] for i in range(n_tasks) for j in range(n_people)]  # the cost of each pair

    # The total cost of the assignments made stays between 0 and the sum of all costs.
    formula.extend(PBEnc.geq(lits=lits, weights=weights, bound=0, vpool=pool).clauses)
    formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=sum(weights),
                             vpool=pool).clauses)

    # The total cost is the cost of each pair that is made. A negative cost is paid
    # when its pair is not made, which changes the total by a fixed amount.
    for lit, w in zip(lits, weights):
        if w > 0:
            formula.append([-lit], weight=w)
        elif w < 0:
            formula.append([lit], weight=-w)

    # The objective in the problem's terms: the total cost of the pairs made (RC2's cost
    # differs from it by a fixed amount when some cost is negative).
    objective = [(w, lit) for lit, w in zip(lits, weights)]

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

# appointment_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `appointment_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/appointment_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python appointment_scheduling.py appointment_scheduling.json

from pyscipopt import Model


def create_model(instance):
    """Schedule n people into n interview slots based on their free-busy schedules
    (here 4 people and 4 slots).

    Every person gets exactly one slot, each slot holds at most one person, and a
    person is only put into a slot in which they are free. With as many people as
    slots, "at most one person per slot" forces every slot to be filled, so each
    slot holds exactly one person.
    This is a satisfaction problem: any valid assignment is an answer, no objective.
    """
    # m[i][j] is 1 when person i is free in slot j, and 0 when busy (instance field "m").
    # Rows are people, columns are slots.
    m = instance["m"]
    people = len(m)     # number of people: the rows of m
    slots = len(m[0])   # number of interview slots: the columns of m

    model = Model("appointment_scheduling")

    # x[i, j] is 1 when person i is assigned to slot j, and 0 when not.
    x = model.addMatrixVar((people, slots), vtype="B", name="x")

    # A busy slot cannot be taken: x[i, j] may be 1 only where m[i][j] is 1 (free).
    model.addMatrixCons(x <= m)

    # Each person is assigned to exactly one slot: every row of x sums to 1.
    model.addMatrixCons(x.sum(axis=1) == 1)

    # Each slot holds at most one person: every column of x sums to at most 1.
    model.addMatrixCons(x.sum(axis=0) <= 1)

    return model, {"x": x}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

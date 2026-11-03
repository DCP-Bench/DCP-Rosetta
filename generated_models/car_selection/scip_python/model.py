# car_selection: a SCIP (Python) model from DCP Rosetta.
# Download the `car_selection.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/car_selection.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python car_selection.py car_selection.json

from pyscipopt import Model


def create_model(instance):
    """Assign participants to cars so that as many assignments as possible are made.

    Each participant is interested in some of the cars and can only be assigned one
    of those. A participant is assigned at most one car, and a car goes to at most
    one participant. Some participants or cars may be left without an assignment.
    """
    # interested[i][j] is 1 when participant i is interested in car j, and 0 when not
    interested = instance["possible_assignments"]
    n = len(interested)      # number of participants: the rows of the interest table
    m = len(interested[0])   # number of cars: the columns of the interest table

    model = Model("car_selection")

    # assign[i][j] is 1 when participant i is assigned car j, and 0 when not.
    # The upper bound taken from the interest table forbids assigning a car the
    # participant is not interested in: a cell with 0 in the table is fixed at 0.
    assign = model.addMatrixVar((n, m), vtype="B", name="assign", ub=interested)

    # Each participant is assigned at most one car. At most, not exactly: a
    # participant may be left without a car.
    model.addMatrixCons(assign.sum(axis=1) <= 1)

    # Each car is assigned to at most one participant. At most, not exactly: a car
    # may be left unassigned.
    model.addMatrixCons(assign.sum(axis=0) <= 1)

    # Maximise the total number of assignments made.
    model.setObjective(assign.sum(), "maximize")

    return model, {"assignments": assign}


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

# session1_five_floors: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_five_floors.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python session1_five_floors.py

from pyscipopt import Model
import numpy as np


def create_model(instance):
    """Five people, Baker, Cooper, Fletcher, Miller and Smith, live one to a floor on the
    first five floors of an apartment house, numbered 1 (the first floor) to 5 (the fifth
    floor). Find the floor of each person, given the clues of the statement.

    The instance file is empty ([]): the statement fixes every number in the problem, so
    `instance` is not read.
    """
    model = Model("session1_five_floors")

    # The rows of `living` are the people in this order: Baker, Cooper, Fletcher, Miller, Smith.
    # The columns are the floors, and the floor number of each column is column + 1.
    FLOOR_NUMBERS = np.arange(1, 6)

    # living[p, f] is 1 when person p lives on floor f + 1, and 0 when not.
    living = model.addMatrixVar((5, 5), vtype="B", name="living")

    # Each person lives on exactly one floor.
    model.addMatrixCons(living.sum(axis=1) == 1)
    # Each floor has exactly one of the five people on it, so the five people live on five
    # different floors. SCIP has no all-different constraint, so the one-hot rows and
    # columns together stand for it.
    model.addMatrixCons(living.sum(axis=0) == 1)

    # The floor number of each person: the sum of the floor numbers of the floor they live on.
    # Floor numbers run from 1 to 5 because the one-hot rows above allow only those columns.
    floor_of = living @ FLOOR_NUMBERS
    baker, cooper, fletcher, miller, smith = floor_of

    # Baker does not live on the fifth floor, so Baker's floor number is at most 4.
    model.addCons(baker <= 4)
    # Cooper does not live on the first floor, so Cooper's floor number is at least 2.
    model.addCons(cooper >= 2)
    # Fletcher lives on neither the fifth floor nor the first, so the floor number is from 2 to 4.
    model.addCons(fletcher >= 2)
    model.addCons(fletcher <= 4)
    # Miller lives on a higher floor than Cooper. SCIP has no strict <, so higher means at
    # least one floor up.
    model.addCons(miller >= cooper + 1)

    # Smith does not live on a floor next to Fletcher's, so the two floor numbers differ by at
    # least 2. SCIP has no != and no absolute value, so the binary smith_above picks the side:
    # when it is 1, Smith is at least two floors above Fletcher, and when it is 0, Fletcher is
    # at least two floors above Smith.
    smith_above = model.addVar(vtype="B", name="smith_above")
    model.addConsIndicator(smith - fletcher >= 2, binvar=smith_above)
    model.addConsIndicator(fletcher - smith >= 2, binvar=smith_above, activeone=False)

    # Fletcher does not live on a floor next to Cooper's, so the two floor numbers differ by at
    # least 2. As above, fletcher_above picks the side: when it is 1, Fletcher is at least two
    # floors above Cooper, and when it is 0, Cooper is at least two floors above Fletcher.
    fletcher_above = model.addVar(vtype="B", name="fletcher_above")
    model.addConsIndicator(fletcher - cooper >= 2, binvar=fletcher_above)
    model.addConsIndicator(cooper - fletcher >= 2, binvar=fletcher_above, activeone=False)

    # The statement asks only where each person lives, so the model has no objective: any
    # floors that meet the clues are an answer.
    return model, {"B": baker, "C": cooper, "F": fletcher, "M": miller, "S": smith}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

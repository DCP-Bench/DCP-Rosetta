# session1_thick_as_thieves: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python session1_thick_as_thieves.py

from pyscipopt import Model, quicksum


def create_model(instance):
    """Inspector Korner's puzzle. Six suspects (Artie, Bill, Crackitt, Dodgy, Edgy and
    Fingers) each made one statement. An innocent suspect tells the truth and a guilty
    one lies, so a suspect is guilty exactly when his statement is false. The inspector
    supposed that at least four of them are innocent, so at most two are guilty. Find
    out who is guilty.

    The instance file is empty ([]), so every fact comes from the problem statement and
    the argument is not read.
    """
    model = Model("session1_thick_as_thieves")

    # One binary per suspect: 1 when that suspect is guilty, 0 when innocent.
    artie = model.addVar(name="artie", vtype="B")  # Artie is guilty
    bill = model.addVar(name="bill", vtype="B")  # Bill is guilty
    crackitt = model.addVar(name="crackitt", vtype="B")  # Crackitt is guilty
    dodgy = model.addVar(name="dodgy", vtype="B")  # Dodgy is guilty
    edgy = model.addVar(name="edgy", vtype="B")  # Edgy is guilty
    fingers = model.addVar(name="fingers", vtype="B")  # Fingers is guilty
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    # The number of guilty suspects, used by the cap and by Edgy's statement.
    guilty_count = quicksum(suspects)

    # The getaway car was barely big enough to hold two, so the inspector reckoned at
    # least four suspects are innocent. The puzzle takes this as a given (an assumption
    # from the statement, not derived): at most two suspects are guilty.
    model.addCons(guilty_count <= 2)

    # An indicator constraint addConsIndicator(ineq, binvar=b) enforces ineq when b = 1,
    # and with activeone=False when b = 0. It takes one inequality, not an equality, so a
    # binary that is 1 exactly when a condition holds needs one indicator for each value.

    # Artie: "It wasn't me." The statement is false exactly when Artie is guilty, so the
    # rule "guilty exactly when the statement is false" holds for either value of artie
    # and adds no constraint.

    # Bill: "Crackitt was in it up to his neck." The statement is true exactly when
    # Crackitt is guilty. Bill is guilty exactly when it is false, that is when Crackitt
    # is innocent.
    model.addCons(bill + crackitt == 1)

    # Crackitt: "No I wasn't." The statement is false exactly when Crackitt is guilty, so
    # the rule holds for either value of crackitt and adds no constraint.

    # Dodgy: "If Crackitt did it, Bill did it with him." The statement is false exactly
    # when Crackitt is guilty and Bill is innocent, that is when crackitt - bill = 1. Both
    # are binaries, so crackitt - bill is at most 1, and it equals 1 exactly when it is at
    # least 1.
    model.addConsIndicator(crackitt - bill >= 1, binvar=dodgy)
    model.addConsIndicator(crackitt - bill <= 0, binvar=dodgy, activeone=False)

    # Edgy: "Nobody did it alone." Read as true when at least two suspects are guilty and
    # false otherwise. So Edgy is guilty exactly when guilty_count is at most 1.
    model.addConsIndicator(guilty_count <= 1, binvar=edgy)
    model.addConsIndicator(guilty_count >= 2, binvar=edgy, activeone=False)

    # Fingers: "That's right: it was Artie and Dodgy together." The statement is true
    # exactly when Artie and Dodgy are both guilty, that is when artie + dodgy = 2. Fingers
    # is guilty exactly when it is false, that is when artie + dodgy is at most 1.
    model.addConsIndicator(artie + dodgy <= 1, binvar=fingers)
    model.addConsIndicator(artie + dodgy >= 2, binvar=fingers, activeone=False)

    # The question asks who is guilty and names no quantity to optimise, so the model has
    # no objective.

    # Each output is the guilt of one suspect: 1 when guilty, 0 when innocent.
    return model, {
        "artie": artie,
        "bill": bill,
        "crackitt": crackitt,
        "dodgy": dodgy,
        "edgy": edgy,
        "fingers": fingers,
    }


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

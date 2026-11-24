# jobs_puzzle: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/jobs_puzzle.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python jobs_puzzle.py

import numpy as np
from pyscipopt import Model

# Column of each job in the holds matrix, in the order the statement lists them.
CHEF, GUARD, NURSE, CLERK, POLICE, TEACHER, ACTOR, BOXER = range(8)


def create_model(instance):
    """Four people hold eight different jobs, two jobs each. Five clues restrict
    who can hold which job. Find which person holds each job.

    The instance file is empty ([]), so the statement fixes every size and
    clue here and the instance argument is not read.
    """
    model = Model("jobs_puzzle")

    # holds[p, j] is 1 when person p holds job j, and 0 when not. Persons are
    # numbered 0-3 and jobs are the columns listed above.
    holds = model.addMatrixVar((4, 8), vtype="B", name="holds")

    # Each job is held by exactly one person.
    model.addMatrixCons(holds.sum(axis=0) == 1)

    # Each person holds exactly two jobs.
    model.addMatrixCons(holds.sum(axis=1) == 2)

    # Clue 1: the nurse is not a teacher, police officer, or clerk, read as
    # no one person holds the nurse job together with one of those three.
    model.addMatrixCons(holds[:, NURSE] + holds[:, TEACHER] <= 1)
    model.addMatrixCons(holds[:, NURSE] + holds[:, POLICE] <= 1)
    model.addMatrixCons(holds[:, NURSE] + holds[:, CLERK] <= 1)

    # Clue 2: the clerk is not the chef, read as no one person holds both.
    model.addMatrixCons(holds[:, CLERK] + holds[:, CHEF] <= 1)

    # Clue 3: person 0 is not the boxer.
    model.addCons(holds[0, BOXER] == 0)

    # Clue 4: person 3 is not the teacher, police officer, or nurse.
    model.addCons(holds[3, TEACHER] == 0)
    model.addCons(holds[3, POLICE] == 0)
    model.addCons(holds[3, NURSE] == 0)

    # Clue 5: person 0, the chef, and the police officer went golfing together,
    # so they are three different people. Person 0 holds neither the chef nor
    # the police officer job, and no one person holds both of those two jobs.
    model.addCons(holds[0, CHEF] == 0)
    model.addCons(holds[0, POLICE] == 0)
    model.addMatrixCons(holds[:, CHEF] + holds[:, POLICE] <= 1)

    # person_of[j] is the index (0-3) of the person holding job j. Each job has
    # exactly one holder, so the weighted sum of holds over the people is that
    # person's index.
    person_of = (holds * np.arange(4).reshape(4, 1)).sum(axis=0)

    # The puzzle asks which person holds which jobs, so there is no objective.
    outputs = {
        "actor": person_of[ACTOR],
        "boxer": person_of[BOXER],
        "chef": person_of[CHEF],
        "clerk": person_of[CLERK],
        "guard": person_of[GUARD],
        "nurse": person_of[NURSE],
        "police_officer": person_of[POLICE],
        "teacher": person_of[TEACHER],
    }
    return model, outputs


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

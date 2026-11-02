# session1_thick_as_thieves: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install cvc5 numpy`) with:
#   python session1_thick_as_thieves.py

import cvc5.pythonic as c5


def create_model(instance):
    """Six suspects were questioned after a robbery. The innocent tell the truth and
    the guilty lie. Who is guilty?"""
    # artie, bill, ...: true when that suspect is guilty
    artie, bill, crackitt, dodgy, edgy, fingers = c5.Bools(
        "artie bill crackitt dodgy edgy fingers"
    )

    # all six suspects
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    # how many suspects are guilty
    n_guilty = c5.Sum([c5.If(suspect, 1, 0) for suspect in suspects])

    solver = c5.Solver()

    # At least four of the six are innocent, so at most two are guilty. At least one is guilty.
    solver.add(
        n_guilty <= 2,
        n_guilty >= 1,
    )

    # what each suspect said, as a statement that is true or false
    statements = [
        c5.Not(artie),                    # ARTIE: "It wasn't me."
        crackitt,                         # BILL: "Crackitt was in it up to his neck."
        c5.Not(crackitt),                 # CRACKITT: "No I wasn't."
        c5.Implies(crackitt, bill),       # DODGY: "If Crackitt did it, Bill did it with him."
        n_guilty != 1,                    # EDGY: "Nobody did it alone."
        c5.And(artie, dodgy),             # FINGERS: "That's right: it was Artie and Dodgy together."
    ]

    # The innocent tell the truth and the guilty lie: a suspect is guilty
    # exactly when their statement is false.
    solver.add([suspect == c5.Not(statement) for suspect, statement in zip(suspects, statements)])

    outputs = {
        "artie": artie, "bill": bill, "crackitt": crackitt,
        "dodgy": dodgy, "edgy": edgy, "fingers": fingers,
    }
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

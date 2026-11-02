# session1_thick_as_thieves: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install z3-solver numpy`) with:
#   python session1_thick_as_thieves.py

import z3


def create_model(instance):
    """Six suspects were questioned after a robbery. The getaway car barely held
    two, so at least four of them are innocent. The innocent suspects tell the
    truth and the guilty ones lie. Which suspects are guilty?"""
    # True when the suspect is guilty.
    suspects = z3.Bools("artie bill crackitt dodgy edgy fingers")
    artie, bill, crackitt, dodgy, edgy, fingers = suspects

    solver = z3.Solver()

    # At most two suspects are guilty.
    solver.add(z3.AtMost(*suspects, 2))

    # What each suspect said, as a claim that is true or false.
    statements = [
        z3.Not(artie),                  # Artie: "It wasn't me."
        crackitt,                       # Bill: "Crackitt was in it up to his neck."
        z3.Not(crackitt),               # Crackitt: "No I wasn't."
        z3.Implies(crackitt, bill),     # Dodgy: "If Crackitt did it, Bill did it with him."
        z3.AtLeast(*suspects, 2),       # Edgy: "Nobody did it alone."
        z3.And(artie, dodgy),           # Fingers: "That's right: it was Artie and Dodgy together."
    ]

    # A suspect is guilty exactly when what they said is false.
    solver.add([guilty == z3.Not(claim) for guilty, claim in zip(suspects, statements)])

    return solver, {"artie": artie, "bill": bill, "crackitt": crackitt,
                    "dodgy": dodgy, "edgy": edgy, "fingers": fingers}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

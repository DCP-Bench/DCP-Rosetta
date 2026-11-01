# session1_thick_as_thieves: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install cpmpy`) with:
#   python session1_thick_as_thieves.py

import cpmpy as cp


def create_model(instance):
    """Six suspects, at most two of them guilty: the innocent tell the truth
    and the guilty lie. Who is guilty?

    The puzzle states its own suspects and statements, so `instance` is unused."""
    # Each variable is true when that suspect is guilty
    artie = cp.boolvar(name="artie")
    bill = cp.boolvar(name="bill")
    crackitt = cp.boolvar(name="crackitt")
    dodgy = cp.boolvar(name="dodgy")
    edgy = cp.boolvar(name="edgy")
    fingers = cp.boolvar(name="fingers")
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    model = cp.Model()
    # The getaway car barely held two, so at most two suspects are guilty.
    model.add(cp.sum(suspects) <= 2)

    # What each suspect said, as a statement that is true or false
    statements = [
        ~artie,                           # ARTIE: "It wasn't me."
        crackitt,                         # BILL: "Crackitt was in it up to his neck."
        ~crackitt,                        # CRACKITT: "No I wasn't."
        crackitt.implies(bill),           # DODGY: "If Crackitt did it, Bill did it with him."
        cp.sum(suspects) > 1,             # EDGY: "Nobody did it alone."
        artie & dodgy,                    # FINGERS: "It was Artie and Dodgy together."
    ]
    # The innocent tell the truth and the guilty lie: a suspect is guilty
    # exactly when their statement is false.
    for suspect, statement in zip(suspects, statements):
        model.add(suspect == ~statement)

    return model, {
        "artie": artie, "bill": bill, "crackitt": crackitt,
        "dodgy": dodgy, "edgy": edgy, "fingers": fingers,
    }


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

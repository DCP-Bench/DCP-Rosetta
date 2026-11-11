# session1_thick_as_thieves: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python session1_thick_as_thieves.py

from pycsp3 import *


def create_model(instance):
    """Following a robbery at Sparkles the Jeweller's, Inspector Korner of the Yard interviewed six of the usual
    suspects. He knew that the getaway car had been barely big enough to hold two, so he reckoned that at least four of
    them were innocent. He also supposed that the innocent ones would tell the truth, while the guilty one or ones would
    lie. If the good inspector's suppositions were correct, who is guilty?"""
    # artie is 1 when Artie is guilty, 0 when he is innocent.
    artie = Var(dom={0, 1})
    # bill is 1 when Bill is guilty, 0 when he is innocent.
    bill = Var(dom={0, 1})
    # crackitt is 1 when Crackitt is guilty, 0 when he is innocent.
    crackitt = Var(dom={0, 1})
    # dodgy is 1 when Dodgy is guilty, 0 when he is innocent.
    dodgy = Var(dom={0, 1})
    # edgy is 1 when Edgy is guilty, 0 when he is innocent.
    edgy = Var(dom={0, 1})
    # fingers is 1 when Fingers is guilty, 0 when he is innocent.
    fingers = Var(dom={0, 1})
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    car_seats = 2  # the getaway car was barely big enough to hold two

    satisfy(
        # The inspector reckoned at least four were innocent, so at most car_seats of them are guilty.
        Sum(suspects) <= car_seats,
        # Someone is guilty: the robbery had a culprit (the statement speaks of "the guilty one or ones").
        Sum(suspects) >= 1,
        # Artie's "It wasn't me" and Crackitt's "No I wasn't" are true exactly when their speakers are innocent,
        # so they add no constraint.
        # Bill's "Crackitt was in it up to his neck" is true exactly when Bill is innocent.
        (bill == 0) == (crackitt == 1),
        # Dodgy's "If Crackitt did it, Bill did it with him" is true exactly when Dodgy is innocent.
        (dodgy == 0) == (crackitt <= bill),
        # Edgy's "Nobody did it alone" is true exactly when Edgy is innocent.
        (edgy == 0) == (Sum(suspects) != 1),
        # Fingers' "it was Artie and Dodgy together" is true exactly when Fingers is innocent.
        (fingers == 0) == And(artie == 1, dodgy == 1, Sum(suspects) == 2),
    )

    return {
        "artie": artie,
        "bill": bill,
        "crackitt": crackitt,
        "dodgy": dodgy,
        "edgy": edgy,
        "fingers": fingers,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

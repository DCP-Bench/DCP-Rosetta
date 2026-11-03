# session1_thick_as_thieves: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_thick_as_thieves.html
# Run it (after `pip install hermax`) with:
#   python session1_thick_as_thieves.py

from hermax.model import Model

SUSPECTS = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]


def create_model(instance):
    """Six suspects were interviewed after a robbery. The getaway car held at most two
    of them, so at least four are innocent. The innocent tell the truth and the guilty
    lie, so each suspect is guilty exactly when his statement is false. Who is guilty?

    The instance carries no data: the puzzle is fixed by the problem statement, so
    `instance` is not read.
    """
    m = Model()

    # guilty[name] is true when that suspect took part in the robbery
    guilty = {name: m.bool(name) for name in SUSPECTS}
    artie, bill, crackitt, dodgy, edgy, fingers = (guilty[name] for name in SUSPECTS)

    # The getaway car held two, so at most two suspects are guilty.
    m &= (sum(1 * guilty[name] for name in SUSPECTS) <= 2)

    # Artie: "It wasn't me." He is guilty exactly when that is false, that is exactly
    # when he is guilty, which holds for either value: the statement adds no constraint.
    # Crackitt: "No I wasn't." Likewise, exactly when he is guilty: no constraint.

    # Bill: "Crackitt was in it up to his neck." False exactly when Crackitt is innocent,
    # so Bill is guilty exactly when Crackitt is innocent.
    m &= (bill | crackitt)
    m &= (~bill | ~crackitt)

    # Dodgy: "If Crackitt did it, Bill did it with him." False exactly when Crackitt is
    # guilty and Bill is innocent. Dodgy is guilty exactly then.
    m &= (~dodgy | crackitt)
    m &= (~dodgy | ~bill)
    m &= (dodgy | ~crackitt | bill)

    # Edgy: "Nobody did it alone." False exactly when at most one suspect is guilty.
    # Edgy is guilty exactly when at most one suspect is guilty.
    m &= ((sum(1 * guilty[name] for name in SUSPECTS) <= 1).iff(edgy))

    # Fingers: "That's right: it was Artie and Dodgy together." False exactly when Artie
    # and Dodgy are not both guilty. Fingers is guilty exactly when that is the case.
    m &= (~fingers | ~artie | ~dodgy)
    m &= (fingers | artie)
    m &= (fingers | dodgy)

    # No objective: the puzzle asks for the guilty suspects, so it is a satisfaction problem.
    return m, guilty


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

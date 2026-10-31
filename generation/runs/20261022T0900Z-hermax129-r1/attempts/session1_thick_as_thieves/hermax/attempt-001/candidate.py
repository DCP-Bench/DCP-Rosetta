from hermax.model import Model


def build(instance):
    m = Model()
    # Each suspect is guilty (True) or innocent (False).
    artie = m.bool("artie")
    bill = m.bool("bill")
    crackitt = m.bool("crackitt")
    dodgy = m.bool("dodgy")
    edgy = m.bool("edgy")
    fingers = m.bool("fingers")
    suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

    # The getaway car held two, and at least four are innocent, so at most two are guilty.
    m &= (sum(suspects) <= 2)

    # The innocent ones tell the truth and the guilty ones lie, so each suspect is guilty
    # exactly when their statement is false.

    # ARTIE: "It wasn't me." This is true exactly when Artie is innocent, so it adds no constraint.

    # BILL: "Crackitt was in it up to his neck." Bill is guilty exactly when Crackitt is innocent.
    m &= (bill | crackitt)
    m &= (~bill | ~crackitt)

    # CRACKITT: "No I wasn't." This is true exactly when Crackitt is innocent, so it adds no constraint.

    # DODGY: "If Crackitt did it, Bill did it with him." The statement is false exactly when
    # Crackitt is guilty and Bill is innocent. Dodgy is guilty exactly when that holds.
    m &= (~dodgy | crackitt)
    m &= (~dodgy | ~bill)
    m &= (~crackitt | bill | dodgy)

    # EDGY: "Nobody did it alone." The statement is false exactly when exactly one is guilty.
    m &= (sum(suspects) == 1).iff(edgy)

    # FINGERS: "It was Artie and Dodgy together." The statement is false unless both are guilty.
    # Fingers is guilty exactly when the statement is false.
    m &= (fingers | artie)
    m &= (fingers | dodgy)
    m &= (~fingers | ~artie | ~dodgy)

    return m, {
        "artie": artie,
        "bill": bill,
        "crackitt": crackitt,
        "dodgy": dodgy,
        "edgy": edgy,
        "fingers": fingers,
    }

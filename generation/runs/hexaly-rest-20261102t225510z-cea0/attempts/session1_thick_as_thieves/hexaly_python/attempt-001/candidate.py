"""Thick as thieves: six suspects, at most two guilty; the innocent tell the truth and the guilty lie."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # guilty[name] = 1 if the suspect was in the robbery
    names = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
    guilty = {name: model.bool() for name in names}
    count = model.sum(list(guilty.values()))
    # The getaway car held two, so at least four were innocent
    model.constraint(count <= 2)

    # What each suspect said, true or false
    said = {
        "artie": model.not_(guilty["artie"]),                           # "It wasn't me."
        "bill": guilty["crackitt"],                                     # "Crackitt was in it."
        "crackitt": model.not_(guilty["crackitt"]),                     # "No I wasn't."
        "dodgy": model.or_(model.not_(guilty["crackitt"]), guilty["bill"]),  # "If Crackitt did it, so did Bill."
        "edgy": count != 1,                                             # "Nobody did it alone."
        "fingers": model.and_(guilty["artie"], guilty["dodgy"], count == 2),  # "It was Artie and Dodgy together."
    }
    # The innocent tell the truth and the guilty lie: a statement is true exactly when its speaker is innocent
    for name in names:
        model.constraint(said[name] == model.not_(guilty[name]))

    return optimizer, guilty

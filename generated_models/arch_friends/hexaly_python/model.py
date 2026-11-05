"""Arch friends: the order (1 to 4) in which Harriet bought four pairs of shoes, and the store of each."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    shoes = {name: model.int(1, 4) for name in ("ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals")}  # the stop (1 to 4) at which each pair of shoes was bought
    stores = {name: model.int(1, 4) for name in ("footfarm", "heelsinahandcart", "theshoepalace", "tootsies")}  # the stop (1 to 4) at which each store was visited
    # Each stop has one pair of shoes and one store: the four values of each group differ
    for group in (list(shoes.values()), list(stores.values())):
        for a in range(4):
            for b in range(a + 1, 4):
                model.constraint(group[a] != group[b])

    # 1. She bought the fuchsia flats at Heels in a Handcart
    model.constraint(shoes["fuchsiaflats"] == stores["heelsinahandcart"])
    # 2. The store visited just after buying the purple pumps (so not the last stop) was not Tootsies
    model.constraint(shoes["purplepumps"] <= 3)
    model.constraint(stores["tootsies"] != shoes["purplepumps"] + 1)
    # 3. The Foot Farm was her second stop
    model.constraint(stores["footfarm"] == 2)
    # 4. Two stops after leaving The Shoe Palace, she bought the suede sandals
    model.constraint(shoes["suedesandals"] == stores["theshoepalace"] + 2)

    return optimizer, {**shoes, **stores}

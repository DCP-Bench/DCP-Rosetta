# arch_friends: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install cpmpy`) with:
#   python arch_friends.py

import cpmpy as cp


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
    pumps, suede sandals) at four different stores (Foot Farm, Heels in a
    Handcart, The Shoe Palace, Tootsies). Work out the order in which she bought
    each pair and where she bought each. The puzzle fixes its own data, so
    instance is not used."""
    # shoes[k] is the stop at which shoe k was bought, from 1 to 4
    shoes = cp.intvar(1, 4, shape=4, name="shoes")
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    # store[k] is the stop at which store k was visited, from 1 to 4. A shoe and
    # a store with the same stop number belong together.
    store = cp.intvar(1, 4, shape=4, name="store")
    footfarm, heelsinahandcart, theshoepalace, tootsies = store

    model = cp.Model()

    # Each stop buys one shoe and visits one store.
    model.add(cp.AllDifferent(shoes))
    model.add(cp.AllDifferent(store))

    # Harriet bought the fuchsia flats at Heels in a Handcart.
    model.add(fuchsiaflats == heelsinahandcart)
    # The store visited just after buying the purple pumps was not Tootsies.
    model.add(purplepumps + 1 != tootsies)
    # The Foot Farm was the second stop.
    model.add(footfarm == 2)
    # The suede sandals were bought two stops after The Shoe Palace.
    model.add(theshoepalace + 2 == suedesandals)

    return model, {
        "ecruespadrilles": ecruespadrilles,
        "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps,
        "suedesandals": suedesandals,
        "footfarm": footfarm,
        "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace,
        "tootsies": tootsies,
    }


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

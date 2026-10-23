"""Arch Friends - a constraint satisfaction problem about shoe shopping.

Four shoes and four stores, with constraints linking them via visit order.
"""

from hermax.model import Model


def build(instance):
    # Problem constants: 4 shoes and 4 stores, values from 1 to 4 representing visit order
    n = 4

    m = Model()

    # Shoes and stores as integer variables from 1 to 4
    ecruespadrilles = m.int("ecruespadrilles", 1, n)
    fuchsiaflats = m.int("fuchsiaflats", 1, n)
    purplepumps = m.int("purplepumps", 1, n)
    suedesandals = m.int("suedesandals", 1, n)

    footfarm = m.int("footfarm", 1, n)
    heelsinahandcart = m.int("heelsinahandcart", 1, n)
    theshoepalace = m.int("theshoepalace", 1, n)
    tootsies = m.int("tootsies", 1, n)

    # All shoes have different visit orders
    shoes = m.int_vector("shoes", n, 1, n)
    shoes_vars = [ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]
    for i, var in enumerate(shoes_vars):
        m &= (var == shoes[i])
    m &= shoes.all_different()

    # All stores have different visit orders
    stores = m.int_vector("stores", n, 1, n)
    stores_vars = [footfarm, heelsinahandcart, theshoepalace, tootsies]
    for i, var in enumerate(stores_vars):
        m &= (var == stores[i])
    m &= stores.all_different()

    # Constraint 1: Harriet bought fuchsia flats at Heels in a Handcart
    m &= (fuchsiaflats == heelsinahandcart)

    # Constraint 2: The store visited just after buying purple pumps was not Tootsies
    m &= (purplepumps + 1 != tootsies)

    # Constraint 3: The Foot Farm was Harriet's second stop
    m &= (footfarm == 2)

    # Constraint 4: Two stops after The Shoe Palace, Harriet bought suede sandals
    m &= (theshoepalace + 2 == suedesandals)

    outputs = {
        "ecruespadrilles": ecruespadrilles,
        "fuchsiaflats": fuchsiaflats,
        "purplepumps": purplepumps,
        "suedesandals": suedesandals,
        "footfarm": footfarm,
        "heelsinahandcart": heelsinahandcart,
        "theshoepalace": theshoepalace,
        "tootsies": tootsies,
    }

    return m, outputs

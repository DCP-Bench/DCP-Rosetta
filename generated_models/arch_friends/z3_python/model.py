# arch_friends: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install z3-solver numpy`) with:
#   python arch_friends.py

import z3


def create_model(instance):
    """Harriet bought four pairs of shoes at four stores, one pair at each stop.
    Work out the order of her stops, and which shoes and which store go with each
    stop."""
    # The stop at which Harriet bought each pair of shoes
    shoes = z3.Ints("ecruespadrilles fuchsiaflats purplepumps suedesandals")
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = shoes
    # The stop at which Harriet visited each store. A pair of shoes and a store
    # with the same stop number were at the same stop.
    stores = z3.Ints("footfarm heelsinahandcart theshoepalace tootsies")
    footfarm, heelsinahandcart, theshoepalace, tootsies = stores
    n = len(shoes)  # the number of stops, one for each pair of shoes

    solver = z3.Solver()
    # Each stop is numbered from 1 to n.
    solver.add([z3.And(v >= 1, v <= n) for v in list(shoes) + list(stores)])
    # Each stop is a different pair of shoes.
    solver.add(z3.Distinct(shoes))
    # Each stop is a different store.
    solver.add(z3.Distinct(stores))
    # Harriet bought the fuchsia flats at Heels in a Handcart.
    solver.add(fuchsiaflats == heelsinahandcart)
    # The store she visited just after buying the purple pumps was not Tootsies.
    solver.add(purplepumps + 1 != tootsies)
    # The Foot Farm was her second stop.
    solver.add(footfarm == 2)
    # The suede sandals were bought two stops after The Shoe Palace.
    solver.add(theshoepalace + 2 == suedesandals)

    return solver, {
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
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

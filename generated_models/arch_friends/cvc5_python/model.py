# arch_friends: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install cvc5 numpy`) with:
#   python arch_friends.py

import cvc5.pythonic as c5


def create_model(instance):
    """Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
    pumps, suede sandals) at four different stores (Foot Farm, Heels in a
    Handcart, The Shoe Palace, Tootsies). Work out the order in which she bought
    each pair and where she bought each."""
    # The stop, from 1 to 4, at which each pair of shoes was bought and each store was visited
    ecruespadrilles, fuchsiaflats, purplepumps, suedesandals = c5.Ints(
        "ecruespadrilles fuchsiaflats purplepumps suedesandals"
    )
    footfarm, heelsinahandcart, theshoepalace, tootsies = c5.Ints(
        "footfarm heelsinahandcart theshoepalace tootsies"
    )
    shoes = [ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]
    stores = [footfarm, heelsinahandcart, theshoepalace, tootsies]

    solver = c5.Solver()

    # There are four stops, numbered 1 to 4.
    solver.add([v >= 1 for v in shoes + stores] + [v <= 4 for v in shoes + stores])

    # Harriet buys one pair of shoes at each stop.
    solver.add(c5.Distinct(shoes))
    # Harriet visits one store at each stop.
    solver.add(c5.Distinct(stores))

    # Harriet bought the fuchsia flats at Heels in a Handcart.
    solver.add(fuchsiaflats == heelsinahandcart)

    # The store she visited just after buying her purple pumps was not Tootsies.
    solver.add(tootsies != purplepumps + 1)

    # The Foot Farm was Harriet's second stop.
    solver.add(footfarm == 2)

    # Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    solver.add(suedesandals == theshoepalace + 2)

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
    return solver, outputs


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

# arch_friends: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python arch_friends.py

from pycsp3 import *


def create_model(instance):
    """Harriet bought four different pairs of shoes, one at each of four stores, in four stops.
    Find the stop at which she bought each shoe and visited each store."""
    n_stops = 4

    # The stop, from 1 to n_stops, at which Harriet bought each shoe.
    ecruespadrilles = Var(dom=range(1, n_stops + 1))
    fuchsiaflats = Var(dom=range(1, n_stops + 1))
    purplepumps = Var(dom=range(1, n_stops + 1))
    suedesandals = Var(dom=range(1, n_stops + 1))

    # The stop, from 1 to n_stops, at which Harriet visited each store.
    footfarm = Var(dom=range(1, n_stops + 1))
    heelsinahandcart = Var(dom=range(1, n_stops + 1))
    theshoepalace = Var(dom=range(1, n_stops + 1))
    tootsies = Var(dom=range(1, n_stops + 1))

    satisfy(
        # She made one purchase at each stop, so the shoes are at different stops.
        AllDifferent(ecruespadrilles, fuchsiaflats, purplepumps, suedesandals),
        # She visited one store at each stop, so the stores are at different stops.
        AllDifferent(footfarm, heelsinahandcart, theshoepalace, tootsies),
        # Harriet bought fuchsia flats at Heels in a Handcart.
        fuchsiaflats == heelsinahandcart,
        # The store she visited just after buying her purple pumps was not Tootsies.
        tootsies != purplepumps + 1,
        # The Foot Farm was Harriet's second stop.
        footfarm == 2,
        # Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
        suedesandals == theshoepalace + 2,
    )

    return {
        "ecruespadrilles": ecruespadrilles,
        "footfarm": footfarm,
        "fuchsiaflats": fuchsiaflats,
        "heelsinahandcart": heelsinahandcart,
        "purplepumps": purplepumps,
        "suedesandals": suedesandals,
        "theshoepalace": theshoepalace,
        "tootsies": tootsies,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

# arch_friends: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install hermax`) with:
#   python arch_friends.py

"""Harriet bought four kinds of shoes (ecru espadrilles, fuchsia flats, purple pumps,
suede sandals) at four different stores (Foot Farm, Heels in a Handcart, The Shoe Palace,
Tootsies), one pair per stop. Find the stop (1 to 4) at which she bought each kind of shoe
and the stop at which she visited each store."""

from hermax.model import Model

# The puzzle is fixed by the problem statement: four shoes, four stores, four stops.
N = 4


def create_model(instance):
    """The instance carries no data: every number comes from the puzzle statement."""
    m = Model()

    # Decision variables: each is the stop number (1 to N) at which that shoe was bought.
    ecruespadrilles = m.int("ecruespadrilles", 1, N)  # stop of the ecru espadrilles
    fuchsiaflats = m.int("fuchsiaflats", 1, N)        # stop of the fuchsia flats
    purplepumps = m.int("purplepumps", 1, N)          # stop of the purple pumps
    suedesandals = m.int("suedesandals", 1, N)        # stop of the suede sandals

    # Decision variables: each is the stop number (1 to N) at which that store was visited.
    footfarm = m.int("footfarm", 1, N)                # stop at the Foot Farm
    heelsinahandcart = m.int("heelsinahandcart", 1, N)  # stop at Heels in a Handcart
    theshoepalace = m.int("theshoepalace", 1, N)      # stop at The Shoe Palace
    tootsies = m.int("tootsies", 1, N)                # stop at Tootsies

    # Each kind of shoe is bought at a different stop, and each store is visited at a different stop.
    m &= m.vector([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]).all_different()
    m &= m.vector([footfarm, heelsinahandcart, theshoepalace, tootsies]).all_different()

    # Clue 1: Harriet bought fuchsia flats at Heels in a Handcart (same stop).
    m &= (fuchsiaflats == heelsinahandcart)

    # Clue 2: the store visited just after buying the purple pumps was not Tootsies.
    # If the pumps were bought at stop v, then Tootsies is not at stop v + 1.
    for v in range(1, N):
        m &= (~(purplepumps == v) | (tootsies != v + 1))

    # Clue 3: the Foot Farm was Harriet's second stop.
    m &= (footfarm == 2)

    # Clue 4: two stops after leaving The Shoe Palace, she bought her suede sandals.
    m &= (theshoepalace + 2 == suedesandals)

    # No objective: the puzzle only asks for an assignment that satisfies the clues.
    return m, {
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
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

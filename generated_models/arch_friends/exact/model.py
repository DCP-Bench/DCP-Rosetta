# arch_friends: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/arch_friends.html
# Run it (after `pip install exact numpy`) with:
#   python arch_friends.py

from exact import Exact


def create_model(instance):
    """Harriet bought four pairs of shoes at four different stores, one pair
    at each stop, and the stops are numbered 1 to 4. Find the stop at which she
    bought each pair and the stop at which she visited each store."""
    n_stops = 4  # Harriet makes four stops, one for each pair of shoes

    solver = Exact()

    shoes = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    stores = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    # Exact identifies its variables by name.
    # at_stop[name][s - 1] is true when that pair of shoes was bought, or that
    # store was visited, at stop s
    at_stop = {}
    for group in (shoes, stores):
        for name in group:
            solver.addVariable(name, 1, n_stops)
            at_stop[name] = [f"{name}_at_{s}" for s in range(1, n_stops + 1)]
            for indicator in at_stop[name]:
                solver.addVariable(indicator, 0, 1)
            # Each shoe or store is at exactly one stop.
            solver.addConstraint([(1, x) for x in at_stop[name]], True, 1, True, 1)
            # The stop number of a shoe or store is the stop it is at.
            solver.addConstraint([(s, at_stop[name][s - 1]) for s in range(1, n_stops + 1)]
                                 + [(-1, name)], True, 0, True, 0)
        # Within each group, every stop is used once.
        for s in range(n_stops):
            solver.addConstraint([(1, at_stop[name][s]) for name in group], True, 1, True, 1)

    # Harriet bought the fuchsia flats at Heels in a Handcart.
    solver.addConstraint([(1, "fuchsiaflats"), (-1, "heelsinahandcart")], True, 0, True, 0)

    # The store visited just after the purple pumps was not Tootsies.
    for s in range(1, n_stops):
        solver.addConstraint([(1, at_stop["purplepumps"][s - 1]), (1, at_stop["tootsies"][s])],
                             False, 0, True, 1)

    # The Foot Farm was Harriet's second stop.
    solver.fix("footfarm", 2)

    # The suede sandals were bought two stops after leaving The Shoe Palace.
    solver.addConstraint([(1, "theshoepalace"), (-1, "suedesandals")], True, -2, True, -2)

    return solver, {name: name for name in shoes + stores}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

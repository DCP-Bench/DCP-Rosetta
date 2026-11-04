# best_host: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install exact numpy`) with:
#   python best_host.py

from exact import Exact


def create_model(instance):
    """Seat six guests round a dinner table so that every guest sits only next to
    guests they get along with."""
    n = 6  # the number of guests, and of seats
    andrew, betty, cara, dave, erica, frank = range(n)

    # prefs[g] lists the guests that guest g will sit next to.
    prefs = [
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ]

    solver = Exact()

    # Exact identifies its variables by name.
    # sits[i][g] is 1 when guest g sits in seat i, and 0 when not
    sits = [[f"seat_{i}_guest_{g}" for g in range(n)] for i in range(n)]
    for row in sits:
        for name in row:
            solver.addVariable(name, 0, 1)

    # Each seat holds one guest.
    for i in range(n):
        solver.addConstraint([(1, name) for name in sits[i]], True, 1, True, 1)

    # Each guest has one seat.
    for g in range(n):
        solver.addConstraint([(1, sits[i][g]) for i in range(n)], True, 1, True, 1)

    # Seats run round the table, so the last seat is next to the first. Two guests in
    # neighbouring seats must each be willing to sit next to the other.
    for i in range(n):
        j = (i + 1) % n
        for a in range(n):
            for b in range(n):
                if b not in prefs[a] or a not in prefs[b]:
                    solver.addConstraint([(1, sits[i][a]), (1, sits[j][b])], False, 0, True, 1)

    # x[i] is the guest in seat i.
    x = [f"x_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(x[i], 0, n - 1)
        # Seat i holds the guest x[i].
        solver.addConstraint([(g, sits[i][g]) for g in range(1, n)] + [(-1, x[i])], True, 0, True, 0)

    return solver, {"x": x}


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

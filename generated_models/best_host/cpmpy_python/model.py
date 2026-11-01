# best_host: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install cpmpy`) with:
#   python best_host.py

import cpmpy as cp


def create_model(instance):
    """Six guests sit around a dinner table, and each guest only accepts two particular
    neighbours. Find a seating order in which every guest sits between two guests they accept."""
    # The guests are numbered 0 to 5: Andrew, Betty, Cara, Dave, Erica, Frank.
    n = 6
    andrew, betty, cara, dave, erica, frank = range(n)

    # prefs[g] lists the two guests that guest g will sit next to (the problem statement fixes them)
    prefs = cp.cpm_array([
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ])

    # x[i] is the guest in seat i; the seats run around the table, so seat 5 is next to seat 0
    x = cp.intvar(0, n - 1, shape=n, name="x")

    model = cp.Model()
    # Every guest has exactly one seat.
    model.add(cp.AllDifferent(x))
    # Both neighbours of the guest in seat i are on that guest's list.
    for i in range(n):
        for neighbour in (x[(i - 1) % n], x[(i + 1) % n]):
            model.add(cp.any(prefs[x[i], j] == neighbour for j in range(2)))

    return model, {"x": x}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

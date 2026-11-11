# best_host: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python best_host.py

from pycsp3 import *


def create_model(instance):
    """Six guests sit around a round table. Some guests do not get along, so each
    guest must sit only next to the two guests they will sit next to. Find a
    seating order around the table with no conflict."""
    n_guests = 6

    # Who each guest will sit next to (a fixed fact of the problem):
    # 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
    neighbours = {
        0: [3, 5],  # Andrew sits only next to Dave and Frank
        1: [2, 4],  # Betty sits only next to Cara and Erica
        2: [1, 5],  # Cara sits only next to Betty and Frank
        3: [0, 4],  # Dave sits only next to Andrew and Erica
        4: [1, 3],  # Erica sits only next to Betty and Dave
        5: [0, 2],  # Frank sits only next to Andrew and Cara
    }
    # Every ordered pair of guests who are allowed to sit next to each other.
    allowed_neighbours = [(a, b) for a in range(n_guests) for b in neighbours[a]]

    # x[seat] is the guest in that seat, seats numbered in order around the table
    x = VarArray(size=n_guests, dom=range(n_guests))

    satisfy(
        # Each guest takes exactly one seat.
        AllDifferent(x),
        # The guests in neighbouring seats are allowed to sit next to each other;
        # the last seat is next to the first one.
        [Table(scope=[x[i], x[(i + 1) % n_guests]], supports=allowed_neighbours) for i in range(n_guests)],
    )

    return {"x": x}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

# best_host: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install cvc5 numpy`) with:
#   python best_host.py

import cvc5.pythonic as c5


def create_model(instance):
    """Six guests sit around a round dinner table, and each guest will only sit next to
    two particular guests. Find a seating order in which the two neighbours of every
    guest are both guests that guest will sit next to."""
    n = 6  # the number of guests, numbered 0 to 5: Andrew, Betty, Cara, Dave, Erica, Frank

    # accepts[g] lists the two guests that guest g will sit next to
    accepts = {
        0: [3, 5],  # Andrew: Dave, Frank
        1: [2, 4],  # Betty: Cara, Erica
        2: [1, 5],  # Cara: Betty, Frank
        3: [0, 4],  # Dave: Andrew, Erica
        4: [1, 3],  # Erica: Betty, Dave
        5: [0, 2],  # Frank: Andrew, Cara
    }

    # every ordered pair of guests who will sit next to each other
    allowed = [(a, b) for a in accepts for b in accepts[a]]

    # x[i] is the guest in seat i; seat 5 is next to seat 0 round the table
    x = [c5.Int(f"x_{i}") for i in range(n)]

    solver = c5.Solver()

    # Each seat holds a guest numbered 0 to 5.
    solver.add([x[i] >= 0 for i in range(n)] + [x[i] <= n - 1 for i in range(n)])

    # Every guest sits in exactly one seat.
    solver.add(c5.Distinct(x))

    # Each two neighbours at the table are guests who will sit next to each other.
    for i in range(n):
        j = (i + 1) % n
        solver.add(c5.Or([c5.And(x[i] == a, x[j] == b) for a, b in allowed]))

    return solver, {"x": x}


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

# best_host: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install z3-solver numpy`) with:
#   python best_host.py

import z3


def create_model(instance):
    """Six guests sit around a round dinner table. Each guest will only sit next to
    two particular guests. Find a seating order in which every guest sits between
    two guests they will sit next to."""
    n = 6  # the number of guests and seats

    # The guests are numbered 0 to 5: Andrew, Betty, Cara, Dave, Erica, Frank.
    andrew, betty, cara, dave, erica, frank = range(n)

    # prefs[g] lists the two guests that guest g will sit next to.
    prefs = [
        [dave, frank],    # Andrew
        [cara, erica],    # Betty
        [betty, frank],   # Cara
        [andrew, erica],  # Dave
        [betty, dave],    # Erica
        [andrew, cara],   # Frank
    ]

    # x[i] is the guest in seat i. The table is round, so seat 0 is next to seat 5.
    x = [z3.Int(f"x_{i}") for i in range(n)]

    solver = z3.Solver()

    # Each seat holds one of the guests 0 to 5.
    solver.add([z3.And(0 <= seat, seat <= n - 1) for seat in x])

    # Each guest takes exactly one seat.
    solver.add(z3.Distinct(x))

    # The two guests beside the guest in seat i are both on that guest's list.
    solver.add([z3.Implies(x[i] == g, z3.Or([neighbour == p for p in prefs[g]]))
                for i in range(n) for g in range(n)
                for neighbour in (x[(i - 1) % n], x[(i + 1) % n])])

    return solver, {"x": x}


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

# best_host: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python best_host.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine

# prefs[g] is the pair of guests that guest g will sit next to.
# 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank
PREFS = [[3, 5], [2, 4], [1, 5], [0, 4], [1, 3], [0, 2]]


def create_model(instance):
    """Six guests sit around a dinner table, and each guest will only sit next to two
    particular guests. Find a seating order in which every guest sits between two guests
    they accept."""
    n_guests = len(PREFS)  # the number of guests, which is also the number of seats

    pool = IDPool()

    # x[i] is the guest sitting in seat i. The table is round, so the last seat is next to the first.
    x = [Integer(f"x_{i}", 0, n_guests - 1, vpool=pool) for i in range(n_guests)]
    engine = IntegerEngine(vars=x, vpool=pool)

    # Every guest has one seat.
    engine.add_alldifferent(x)
    cnf = engine.clausify()

    # Guests in neighbouring seats must accept each other, so two guests who do not accept
    # each other are ruled out as neighbours.
    for i in range(n_guests):
        j = (i + 1) % n_guests
        for a in range(n_guests):
            for b in range(n_guests):
                if b not in PREFS[a] or a not in PREFS[b]:
                    cnf.append([-x[i].equals(a), -x[j].equals(b)])

    return cnf, {"x": x}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

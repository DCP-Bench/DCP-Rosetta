# circular_table_averbach_1_2: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python circular_table_averbach_1_2.py

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English, French) sit
    round a circular table and each passes cards to the person on their right. Find the
    nationality of each player from the passing clues."""
    pool = IDPool()
    names = ["x", "y", "z", "american", "english", "french"]  # the three players and the three nationalities
    # Seats are numbered 0, 1 and 2 around the table, and seat b + 1 (mod 3) is to the right of
    # seat b. seats[name] is the seat of that player or nationality, so the same seat number for
    # a player and a nationality is the same person.
    seats = {name: Integer(name, 0, 2, vpool=pool) for name in names}
    engine = IntegerEngine(vars=list(seats.values()), vpool=pool)

    # seat a is immediately to the right of seat b
    def right_to(a, b):
        for seat in range(3):
            cnf.append([-seats[b].equals(seat), seats[a].equals((seat + 1) % 3)])

    # The three players sit in different seats.
    engine.add_alldifferent([seats["x"], seats["y"], seats["z"]])
    # The three nationalities sit in different seats.
    engine.add_alldifferent([seats["american"], seats["english"], seats["french"]])

    cnf = engine.clausify()

    # Y passed three hearts to the American, so the American sits to the right of Y.
    right_to("american", "y")
    # X passed to the person who passed to the Frenchwoman, so X sits to the right of the Frenchwoman.
    right_to("x", "french")

    return cnf, seats


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

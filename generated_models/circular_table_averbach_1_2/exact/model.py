# circular_table_averbach_1_2: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install exact numpy`) with:
#   python circular_table_averbach_1_2.py

from exact import Exact


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English and French) sit round
    a table and each passes cards to the person on their right. Find the seat of each player and of
    each nationality, given that Y passed to the American and X passed to the person who passed to
    the Frenchwoman."""
    n_seats = 3                                                # seats around the table, numbered 0 to 2
    players = ["x", "y", "z"]                                  # the players X, Y and Z
    nationalities = ["american", "english", "french"]          # the three nationalities

    solver = Exact()

    # Exact identifies its variables by name.
    # The seat of each player and of each nationality is one of the seats.
    for name in players + nationalities:
        solver.addVariable(name, 0, n_seats - 1)

    # a sits immediately to the right of b: a is one seat past b, or b is the last seat and a the first.
    def right_to(a, b):
        wraps = f"{a}_right_of_{b}_wraps"                      # 1 when a is the first seat and b the last
        solver.addVariable(wraps, 0, 1)
        solver.addConstraint([(1, a), (-1, b), (n_seats, wraps)], True, 1, True, 1)

    # sits[name][seat] is 1 when that player or nationality sits in that seat, and 0 when not
    sits = {name: [f"{name}_sits_{seat}" for seat in range(n_seats)] for name in players + nationalities}
    for name in players + nationalities:
        for flag in sits[name]:
            solver.addVariable(flag, 0, 1)

    for name in players + nationalities:
        # Each player or nationality sits in exactly one seat, and that seat is its number.
        solver.addConstraint([(1, sits[name][seat]) for seat in range(n_seats)], True, 1, True, 1)
        solver.addConstraint([(seat, sits[name][seat]) for seat in range(n_seats)] + [(-1, name)],
                             True, 0, True, 0)

    # Each seat is taken by one player and by one nationality.
    for group in (players, nationalities):
        for seat in range(n_seats):
            solver.addConstraint([(1, sits[name][seat]) for name in group], True, 1, True, 1)

    # The American sits to the right of Y, since Y passed to the American.
    right_to("american", "y")
    # X sits to the right of the Frenchwoman: X passed to the person who passed to her, two seats along.
    right_to("x", "french")

    return solver, {name: name for name in players + nationalities}


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

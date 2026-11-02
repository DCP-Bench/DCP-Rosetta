# circular_table_averbach_1_2: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install z3-solver numpy`) with:
#   python circular_table_averbach_1_2.py

import z3


def create_model(instance):
    """Three players (X, Y, Z) of different nationalities (American, English, French) sit around
    a circular table playing Hearts, each passing three cards to the person on their right.
    Y passed three hearts to the American; X passed the queen of spades and two diamonds to the
    person who passed their cards to the Frenchwoman. Determine the nationality of each person."""
    n = 3  # the number of players, and of seats around the table

    # seat a is immediately to the right of seat b; seat s + 1 is to the right of seat s,
    # and seat 0 is to the right of seat 2
    def right_of(a, b):
        return a == (b + 1) % n

    # the seats of X, Y and Z
    x, y, z = z3.Ints("x y z")
    # the seats of the American, the English and the French players
    american, english, french = z3.Ints("american english french")

    solver = z3.Solver()

    # Each seat is one of the three seats around the table.
    solver.add([z3.And(s >= 0, s <= n - 1) for s in [x, y, z, american, english, french]])

    # The three players sit in three different seats.
    solver.add(z3.Distinct(x, y, z))
    # The three nationalities sit in three different seats.
    solver.add(z3.Distinct(american, english, french))

    # Y passed three hearts to the American, so the American sits on Y's right.
    solver.add(right_of(american, y))
    # X's cards went to the person who passed to the Frenchwoman, so X sits on the Frenchwoman's right.
    solver.add(right_of(x, french))

    return solver, {"x": x, "y": y, "z": z,
                    "american": american, "english": english, "french": french}


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

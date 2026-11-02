# circular_table_averbach_1_2: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install cvc5 numpy`) with:
#   python circular_table_averbach_1_2.py

import cvc5.pythonic as c5


def right(p):
    # The seat on the right of seat p. The seats go round the table in order, so seat 0 is right of seat 2.
    return c5.If(p == 2, 0, p + 1)


def create_model(instance):
    """Three players, X, Y and Z, of different nationalities (American, English and French) sit
    round a circular table playing Hearts, and each passes three cards to the person on their right.
    Y passed three hearts to the American, and X passed the queen of spades and two diamonds to the
    person who passed their cards to the Frenchwoman. Determine the nationality of each person."""
    # x, y and z are the seats of X, Y and Z
    x, y, z = c5.Ints("x y z")
    # american, english and french are the seats of the American, the English and the French player
    american, english, french = c5.Ints("american english french")
    seats = [x, y, z, american, english, french]

    solver = c5.Solver()

    # Every seat is one of the three seats, 0 to 2.
    solver.add([c5.And(s >= 0, s <= 2) for s in seats])

    # X, Y and Z sit in different seats.
    solver.add(c5.Distinct([x, y, z]))

    # The American, the English and the French player sit in different seats.
    solver.add(c5.Distinct([american, english, french]))

    # Y passed three hearts to the American, so the American sits on Y's right.
    solver.add(american == right(y))

    # X passed to the person who passed to the Frenchwoman, so the Frenchwoman sits two seats to the right of X.
    solver.add(french == right(right(x)))

    outputs = {
        "x": x,
        "y": y,
        "z": z,
        "american": american,
        "english": english,
        "french": french,
    }
    return solver, outputs


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

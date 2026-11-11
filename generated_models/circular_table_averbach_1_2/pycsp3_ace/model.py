# circular_table_averbach_1_2: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python circular_table_averbach_1_2.py

from pycsp3 import *


def create_model(instance):
    """Three players X, Y and Z of different nationalities (American, English, French) sit
    around a circular table playing Hearts. Each passed three cards to the person on their
    right. Y passed three hearts to the American; X passed the queen of spades and two
    diamonds to the person who passed their cards to the Frenchwoman. Find the nationality
    of each person."""
    n_people = 3  # three players, seated round the table; seat 1 is right of seat 0, and so on

    # x: the seat of player X (seats are numbered 0 to n_people - 1)
    x = Var(dom=range(n_people))
    # y: the seat of player Y
    y = Var(dom=range(n_people))
    # z: the seat of player Z
    z = Var(dom=range(n_people))

    # american: the seat of the American
    american = Var(dom=range(n_people))
    # english: the seat of the Englishman
    english = Var(dom=range(n_people))
    # french: the seat of the Frenchwoman
    french = Var(dom=range(n_people))

    satisfy(
        # X, Y and Z sit in three different seats.
        AllDifferent(x, y, z),
        # The American, the Englishman and the Frenchwoman are three different people.
        AllDifferent(american, english, french),
        # Y passed three hearts to the American, so the American sits on the right of Y,
        # the seat (y + 1) % n_people.
        american == (y + 1) % n_people,
        # X passed to the person P who passed to the Frenchwoman. P sits on the right of X,
        # and the Frenchwoman on the right of P, so she sits two seats right of X: (x + 2) % n_people.
        french == (x + 2) % n_people,
    )

    return {"american": american, "english": english, "french": french, "x": x, "y": y, "z": z}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

# circular_table_averbach_1_2: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install cpmpy`) with:
#   python circular_table_averbach_1_2.py

import cpmpy as cp


def create_model(instance):
    """Three players (X, Y, Z) of different nationalities (American, English, French)
    sit around a circular table playing Hearts, each passing three cards to the person
    on their right. Y passed three hearts to the American; X passed the queen of spades
    and two diamonds to the person who passed their cards to the Frenchwoman.
    Determine the nationality of each person."""
    n = 3  # players, and seats around the table

    # Seats are numbered 0, 1, 2 around the table, and seat s + 1 is to the right of
    # seat s (seat 0 is to the right of seat 2).
    def right_of(a, b):
        # seat a is immediately to the right of seat b
        return a == (b + 1) % n

    # players[0], players[1], players[2] are the seats of X, Y, Z
    players = cp.intvar(0, n - 1, shape=n, name="players")
    x, y, z = players

    # nationalities[0], [1], [2] are the seats of the American, the Englishwoman, the Frenchwoman
    nationalities = cp.intvar(0, n - 1, shape=n, name="nationalities")
    american, english, french = nationalities

    model = cp.Model()

    # The three players sit in three different seats.
    model.add(cp.AllDifferent(players))

    # The three nationalities sit in three different seats.
    model.add(cp.AllDifferent(nationalities))

    # Y passed three hearts to the American: the American is on Y's right.
    model.add(right_of(american, y))

    # X passed to the person (on X's right) who passed to the Frenchwoman, so the
    # Frenchwoman is two seats to the right of X; at a table of three that puts X on
    # the Frenchwoman's right.
    model.add(right_of(x, french))

    return model, {"x": x, "y": y, "z": z,
                   "american": american, "english": english, "french": french}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

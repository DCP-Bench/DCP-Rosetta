# circular_table_averbach_1_2: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circular_table_averbach_1_2.html
# Run it (after `pip install hermax`) with:
#   python circular_table_averbach_1_2.py

from hermax.model import Model


def create_model(instance):
    """Three players X, Y, Z of three nationalities (American, English, French) sit round a
    circular table, seats 0, 1, 2, with seat b+1 to the right of seat b. Each player passed
    three cards to the person on their right. Y passed to the American, and X passed to the
    person who passed to the Frenchwoman. Find the seat of every player and every nationality.
    The statement fixes all the data, so the instance carries nothing the model reads."""
    m = Model()

    # The seats of the players X, Y, Z: each seat 0..2 is taken by exactly one player.
    x = m.int("x", 0, 2)  # x: the seat of player X
    y = m.int("y", 0, 2)  # y: the seat of player Y
    z = m.int("z", 0, 2)  # z: the seat of player Z
    m &= m.vector([x, y, z]).all_different()

    # The seats of the nationalities: each seat 0..2 is taken by exactly one nationality.
    # The same seat number in the player and nationality outputs denotes the same person.
    american = m.int("american", 0, 2)  # american: the seat of the American
    english = m.int("english", 0, 2)    # english: the seat of the Englishman
    french = m.int("french", 0, 2)      # french: the seat of the Frenchwoman
    m &= m.vector([american, english, french]).all_different()

    # A seat pair (b, a) where a is immediately to the right of b: seat b+1 is right of seat b.
    right_of = [(0, 1), (1, 2), (2, 0)]

    # Y passed three cards to the American, so the American sits immediately to the right of Y.
    m &= m.table([y, american], allowed=right_of)

    # X passed to the person who passed to the Frenchwoman. That person sits immediately to the
    # left of the Frenchwoman, so X sits immediately to the right of the Frenchwoman.
    m &= m.table([french, x], allowed=right_of)

    # There is no objective: the statement asks only for the seating.
    return m, {"x": x, "y": y, "z": z, "american": american, "english": english, "french": french}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

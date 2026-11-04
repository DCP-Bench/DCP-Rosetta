# set_game: a Z3 (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python set_game.py set_game.json

import z3


def create_model(instance):
    """Set card game: among the cards on the table, find three cards that form a set.
    For each of the four features (number, fill, colour, shape), the three cards must
    show that feature either all the same or all different."""
    cards = instance["cards_data"]  # cards[c] is [number, fill, colour, shape] of card c
    n_cards = len(cards)            # the number of cards on the table
    n_features = len(cards[0])      # the number of features on each card

    # The value of feature f on the card at position index on the table.
    def feature_of(index, f):
        value = cards[n_cards - 1][f]
        for k in range(n_cards - 2, -1, -1):
            value = z3.If(index == k, cards[k][f], value)
        return value

    # winning_cards[k] is the position on the table of the k-th card of the set
    winning_cards = [z3.Int(f"winning_{k}") for k in range(3)]

    solver = z3.Solver()

    # Each chosen position is a card on the table, and the three are different cards.
    solver.add([z3.And(index >= 0, index < n_cards) for index in winning_cards])
    solver.add(z3.Distinct(winning_cards))

    # For each feature, the three cards show it all the same or all different.
    for f in range(n_features):
        a, b, c = (feature_of(index, f) for index in winning_cards)
        solver.add(z3.Or(z3.And(a == b, b == c), z3.Distinct(a, b, c)))

    return solver, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

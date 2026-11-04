# set_game: a cvc5 (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python set_game.py set_game.json

import cvc5.pythonic as c5


def create_model(instance):
    """Set card game: from the cards on the table, find three cards that form a set.
    For each of the four features (number, fill, color, shape), the three cards
    must show it all the same or all different."""
    cards = instance["cards_data"]  # cards[c]: the number, fill, color and shape of card c
    n_cards = len(cards)            # the number of cards on the table

    # card_k is the position on the table of the k-th card of the set
    winning_cards = [c5.Int(f"card_{k}") for k in range(3)]

    def feature_on(card, f):
        # the value of feature f on the card at position card
        value = cards[n_cards - 1][f]
        for k in range(n_cards - 2, -1, -1):
            value = c5.If(card == k, cards[k][f], value)
        return value

    solver = c5.Solver()

    # The three cards are different cards on the table.
    solver.add(c5.Distinct(winning_cards))
    # Each card of the set is on the table.
    solver.add([c5.And(card >= 0, card <= n_cards - 1) for card in winning_cards])
    # For each feature, the three cards show it all the same or all different.
    for f in range(4):
        shown = [feature_on(card, f) for card in winning_cards]
        solver.add(c5.Or(c5.And(shown[0] == shown[1], shown[1] == shown[2]), c5.Distinct(shown)))

    return solver, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

# set_game: a CPMpy model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python set_game.py set_game.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """Set card game: from the cards on the table, find three cards that form a set.
    For each of the four features (number, fill, colour, shape), the three cards
    must show it all the same or all different."""
    # cards[c] holds [number, fill, colour, shape] of card c, as integer codes.
    # The other fields of the instance only name those codes.
    cards = np.array(instance["cards_data"])
    num_cards = len(cards)

    # winning_cards[k] is the (0-based) index of the k-th card of the set
    winning_cards = cp.intvar(0, num_cards - 1, shape=3, name="winning_cards")

    model = cp.Model()
    # The three cards are different cards.
    model.add(cp.AllDifferent(winning_cards))

    # For each feature, the three cards show it all the same or all different
    # (never two the same and one different).
    for feature in range(4):
        column = cp.cpm_array(cards[:, feature])  # this feature on every card
        shown = [column[card] for card in winning_cards]  # this feature on the three chosen cards
        model.add(cp.AllEqual(shown) | cp.AllDifferent(shown))

    return model, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

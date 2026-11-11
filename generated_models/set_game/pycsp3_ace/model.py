# set_game: a PyCSP3 model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python set_game.py set_game.json

from pycsp3 import *


def create_model(instance):
    """Find three different cards of a Set deck that form a set: for each of the four
    features (number, shading, colour, shape) the three cards show that feature either
    all the same or all different."""
    cards = instance["cards_data"]  # cards[i] is [number, shading, colour, shape] of card i, as codes
    n_cards = len(cards)
    n_features = len(cards[0])
    set_size = 3  # a set is three cards

    # The feature codes that occur on the cards: each feature of a chosen card takes one of them.
    codes = sorted({code for card in cards for code in card})

    # winning_cards[k] is the index of the k-th card of the set
    winning_cards = VarArray(size=set_size, dom=range(n_cards))

    # card_features[k][f] is feature f of the k-th card of the set
    card_features = VarArray(size=[set_size, n_features], dom=codes)

    satisfy(
        # The three cards are different cards.
        AllDifferent(winning_cards),
        # The features of each chosen card are those of the card with that index.
        [Table(scope=[winning_cards[k]] + list(card_features[k]),
               supports=[(i, *card) for i, card in enumerate(cards)])
         for k in range(set_size)],
        # For each feature the three cards are all the same or all different, so the number of distinct values is not two.
        [NValues(card_features[:, f]) != 2 for f in range(n_features)],
    )

    return {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

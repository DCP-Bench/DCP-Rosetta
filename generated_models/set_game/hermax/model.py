# set_game: a hermax (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install hermax`):
#   python set_game.py set_game.json

from hermax.model import Model


def create_model(instance):
    """Find a set in Set: three cards from the table such that, for each of the four
    features (number, shading, colour, shape), the three cards show either the same
    value or three different values. Report the indices of the three cards."""
    cards = instance["cards_data"]  # cards[c] = [number, shading, colour, shape] of card c, 0-based
    n_cards = len(cards)
    n_features = 4  # number, shading (the fill field), colour, shape

    m = Model()

    # winning_cards[k] is the index of the k-th card of the set
    winning_cards = m.int_vector("winning_cards", 3, 0, n_cards - 1)
    # The three cards are three different cards on the table.
    m &= winning_cards.all_different()

    for f in range(n_features):
        # the values feature f takes among the cards on the table
        values = sorted({card[f] for card in cards})
        # shown[k] is the value of feature f on the k-th card of the set
        shown = [m.int(f"feature_{f}_card_{k}", values[0], values[-1]) for k in range(3)]

        # Link each card of the set to its own feature value: the card chosen for
        # slot k shows feature f with the value it has on the table.
        for k in range(3):
            m &= m.table([winning_cards[k], shown[k]],
                         allowed=[(c, cards[c][f]) for c in range(n_cards)])

        # The set rule for feature f: the three values are all the same or all different,
        # so the allowed triples are those with x == y == z or with x, y, z pairwise different.
        allowed_triples = [(x, y, z) for x in values for y in values for z in values
                           if x == y == z or len({x, y, z}) == 3]
        m &= m.table(shown, allowed=allowed_triples)

    return m, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

"""Set game: pick three of the cards so that each of the four features is all the same or all different."""
import hexaly.optimizer as hx


def build(instance):
    cards = instance["cards_data"]  # cards[i] holds the value of each of the four features of card i
    n, features = len(cards), len(cards[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # winning_cards are three different cards, listed in increasing order
    winning_cards = [model.int(0, n - 1) for _ in range(3)]
    model.constraint(winning_cards[0] < winning_cards[1])
    model.constraint(winning_cards[1] < winning_cards[2])

    for f in range(features):
        column = model.array([cards[i][f] for i in range(n)])
        a, b, c = (model.at(column, w) for w in winning_cards)
        # The three cards show this feature all the same, or all different
        model.constraint(model.or_(model.and_(a == b, b == c), model.and_(a != b, b != c, a != c)))

    return optimizer, {"winning_cards": winning_cards}

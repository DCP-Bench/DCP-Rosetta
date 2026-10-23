from hermax.model import Model


def build(instance):
    cards = instance["cards_data"]  # one row per card: number, fill, color, shape
    n_cards = len(cards)
    n_features = 4  # fixed by the game

    m = Model()

    # The three winning cards, as indices into the card list.
    idx = m.int_vector("card", 3, 0, n_cards - 1)

    # Three different cards.
    m &= idx.all_different()

    # value[j][f]: feature f of the j-th chosen card, read from the table
    # with the card index as a lookup.
    value = [[None] * n_features for _ in range(3)]
    for j in range(3):
        for f in range(n_features):
            column = [cards[k][f] for k in range(n_cards)]
            v = m.int(f"value_{j}_{f}", min(column), max(column))
            m &= ((column @ idx[j]) == v)
            value[j][f] = v

    # For each feature the three cards are all the same or all different.
    # Let same_ab, same_bc, same_ac say whether each pair agrees on the feature.
    # All same gives all three true, all different gives all three false, and
    # any other pattern (exactly one pair agrees) is mixed, so the three
    # Booleans must be equal.
    for f in range(n_features):
        a, b, c = value[0][f], value[1][f], value[2][f]
        same_ab, same_bc, same_ac = m.bool(), m.bool(), m.bool()
        m &= (a == b).iff(same_ab)
        m &= (b == c).iff(same_bc)
        m &= (a == c).iff(same_ac)
        # The Booleans are equal: same_ab == same_bc == same_ac.
        m &= (same_ab | ~same_bc)
        m &= (~same_ab | same_bc)
        m &= (same_bc | ~same_ac)
        m &= (~same_bc | same_ac)

    return m, {"winning_cards": idx}

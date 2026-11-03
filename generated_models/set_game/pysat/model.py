# set_game: a PySAT (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python set_game.py set_game.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Set card game: among the cards on the table, find three that form a set. For each of the
    four features (number, fill, colour and shape), the three cards must show that feature all
    the same or all different."""
    cards = instance["cards_data"]  # cards[c] holds the features of card c: number, fill, colour and shape
    n_cards = len(cards)            # the number of cards on the table
    n_features = len(cards[0])      # the features on each card
    set_size = 3                    # a set is three cards

    pool = IDPool()
    # winning_cards[k] is the card on the table that is card k of the set
    winning_cards = [Integer(f"winning_{k}", 0, n_cards - 1, vpool=pool) for k in range(set_size)]
    engine = IntegerEngine(vars=winning_cards, vpool=pool)

    # The three cards are different cards.
    engine.add_alldifferent(winning_cards)
    cnf = engine.clausify()

    # For each feature, the three cards show it all the same or all different. So two cards that
    # agree on a feature rule out a third card that disagrees. odd is the card that disagrees,
    # first and second are the other two.
    for feature in range(n_features):
        for odd in range(set_size):
            first, second = [k for k in range(set_size) if k != odd]
            for card_a in range(n_cards):
                for card_b in range(n_cards):
                    if cards[card_a][feature] != cards[card_b][feature]:
                        continue
                    for card_odd in range(n_cards):
                        if cards[card_odd][feature] != cards[card_a][feature]:
                            cnf.append([-winning_cards[first].equals(card_a),
                                        -winning_cards[second].equals(card_b),
                                        -winning_cards[odd].equals(card_odd)])

    return cnf, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

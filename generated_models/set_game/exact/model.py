# set_game: an Exact (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python set_game.py set_game.json

from exact import Exact


def create_model(instance):
    """Set card game: among the cards on the table, find three that form a set. For each of the
    four features (number, fill, colour, shape), the three cards must show it all the same or all
    different."""
    # cards[c] holds the codes of card c for number, fill, colour and shape, in that order.
    # The other fields of the instance name those codes.
    cards = instance["cards_data"]
    n_cards = len(cards)  # the number of cards on the table
    n_features = 4        # the four features of a card

    solver = Exact()

    # Exact identifies its variables by name.
    # chosen[k][c] is 1 when the k-th card of the set is card c, and 0 when not
    chosen = [[f"chosen_{k}_{c}" for c in range(n_cards)] for k in range(3)]
    # winning_cards[k] is the position of the k-th card of the set on the table
    winning_cards = [f"winning_{k}" for k in range(3)]
    for k in range(3):
        solver.addVariable(winning_cards[k], 0, n_cards - 1)
        for name in chosen[k]:
            solver.addVariable(name, 0, 1)
        # Each card of the set is exactly one card on the table.
        solver.addConstraint([(1, name) for name in chosen[k]], True, 1, True, 1)
        # winning_cards[k] is the position of the card chosen as the k-th card.
        solver.addConstraint([(c, chosen[k][c]) for c in range(1, n_cards)] + [(-1, winning_cards[k])],
                             True, 0, True, 0)

    # The three cards of the set are different cards.
    for c in range(n_cards):
        solver.addConstraint([(1, chosen[k][c]) for k in range(3)], False, 0, True, 1)

    for f in range(n_features):
        for v in sorted({card[f] for card in cards}):
            # shows[k] is 1 when the k-th card of the set has value v for this feature, and 0 when not
            shows = []
            for k in range(3):
                name = f"shows_{f}_{v}_{k}"
                solver.addVariable(name, 0, 1)
                # shows[k] is 1 exactly when the k-th card has value v for this feature.
                solver.addConstraint([(1, name)] + [(-1, chosen[k][c]) for c in range(n_cards) if cards[c][f] == v],
                                     True, 0, True, 0)
                shows.append(name)
            # If two cards of the set have value v for this feature, the third has it too.
            for a, b, c in ((0, 1, 2), (0, 2, 1), (1, 2, 0)):
                solver.addConstraint([(1, shows[a]), (1, shows[b]), (-1, shows[c])], False, 0, True, 1)

    return solver, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

# set_game: a Choco-solver (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python set_game.py set_game.json

from pychoco.model import Model


def create_model(instance):
    """Set card game: among the cards on the table, find three that form a set. For each
    of the four features (number, fill, colour, shape), the three cards must show that
    feature all the same or all different."""
    # The values of each feature are numbers ONE, TWO, THREE; colors RED, PURPLE, GREEN;
    # shapes DIAMOND, RECT, ELLIPSE; and fills FULL, EMPTY, STRIPED, coded 1, 2 and 3.
    cards = instance["cards_data"]  # cards[c] holds the number, fill, colour and shape of card c
    n_cards = len(cards)            # the number of cards on the table
    n_features = 4                  # number, fill, colour and shape

    model = Model()

    # winning_cards[k] is the index of the k-th card of the set
    winning_cards = [model.intvar(0, n_cards - 1, name=f"winning_{k}") for k in range(3)]

    # The three cards are different cards.
    model.all_different(winning_cards).post()

    for feature in range(n_features):
        feature_of_card = [card[feature] for card in cards]
        low, high = min(feature_of_card), max(feature_of_card)
        # shown[k] is this feature on the k-th card of the set
        shown = []
        for k in range(3):
            value = model.intvar(low, high, name=f"feature_{feature}_card_{k}")
            model.element(value, feature_of_card, winning_cards[k]).post()
            shown.append(value)
        # The three cards show this feature all the same or all different.
        model.or_([model.all_equal(shown), model.all_different(shown)]).post()

    return model, {"winning_cards": winning_cards}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

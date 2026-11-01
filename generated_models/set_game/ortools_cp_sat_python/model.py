# set_game: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install ortools`):
#   python set_game.py set_game.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Set card game: among the cards on the table, find three that form a set.
    For each of the four features (number, fill, colour, shape), the three cards
    must show that feature all the same or all different."""
    cards = instance["cards_data"]  # cards[c] holds the number, fill, colour and shape of card c
    n_cards = len(cards)            # the number of cards on the table

    model = cp_model.CpModel()

    # winning_cards[k] is which card on the table is the k-th card of the set
    winning_cards = [model.new_int_var(0, n_cards - 1, f"winning_{k}") for k in range(3)]
    # The three cards are different cards.
    model.add_all_different(winning_cards)

    # For each feature, the three cards show it all the same or all different,
    # never two the same and one different.
    for feature in range(4):
        # the value of this feature on each card on the table
        feature_of_card = [card[feature] for card in cards]
        # the lowest and the highest value of this feature
        low, high = min(feature_of_card), max(feature_of_card)
        # shown[k] is this feature on the k-th card of the set
        shown = []
        for k in range(3):
            value = model.new_int_var(low, high, f"feature_{feature}_card_{k}")
            model.add_element(winning_cards[k], feature_of_card, value)
            shown.append(value)
        # all_equal is true when the three cards show the feature all the same
        all_equal = model.new_bool_var(f"all_equal_{feature}")
        # Equal values when all_equal, different values otherwise.
        model.add(shown[0] == shown[1]).only_enforce_if(all_equal)
        model.add(shown[1] == shown[2]).only_enforce_if(all_equal)
        model.add(shown[0] != shown[1]).only_enforce_if(~all_equal)
        model.add(shown[1] != shown[2]).only_enforce_if(~all_equal)
        model.add(shown[0] != shown[2]).only_enforce_if(~all_equal)

    return model, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

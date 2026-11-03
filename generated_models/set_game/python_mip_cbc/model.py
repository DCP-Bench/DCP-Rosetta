# set_game: a Python-MIP (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python set_game.py set_game.json

import mip


def create_model(instance):
    """Set card game: from the cards on the table, find three cards that form a set.
    For each of the four features (number, fill, colour, shape), the three cards
    must show it all the same or all different."""
    # cards[c] holds the four feature values of card c, each 1, 2 or 3. The other
    # instance fields only name those values, so the model does not read them.
    cards = instance["cards_data"]
    n_cards = len(cards)  # the number of cards on the table

    model = mip.Model(solver_name="CBC")

    # chosen[k][c] is 1 when card c is the k-th card of the set, and 0 when not.
    chosen = [
        [model.add_var(f"chosen_{k}_{c}", var_type=mip.BINARY) for c in range(n_cards)]
        for k in range(3)
    ]
    # winning_cards[k] is the 0-based index of the k-th card of the set.
    winning_cards = [
        model.add_var(f"winning_{k}", lb=0, ub=n_cards - 1, var_type=mip.INTEGER)
        for k in range(3)
    ]

    for k in range(3):
        # Exactly one card on the table is the k-th card, and its index is the output.
        model.add_constr(mip.xsum(chosen[k]) == 1)
        model.add_constr(winning_cards[k] == mip.xsum(c * chosen[k][c] for c in range(n_cards)))

    # The three cards are different cards: each card is chosen at most once.
    for c in range(n_cards):
        model.add_constr(mip.xsum(chosen[k][c] for k in range(3)) <= 1)

    # For each feature, the three cards show it all the same or all different. Read the
    # values 1, 2, 3 as residues mod 3: three values are all the same or all different
    # exactly when they sum to a multiple of 3.
    for f in range(4):
        # t is the total of this feature over the three cards, divided by 3.
        t = model.add_var(f"t_{f}", lb=0, ub=3, var_type=mip.INTEGER)
        model.add_constr(
            mip.xsum(cards[c][f] * chosen[k][c] for k in range(3) for c in range(n_cards))
            == 3 * t
        )

    return model, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

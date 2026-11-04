# set_game: a PuLP (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python set_game.py set_game.json

import pulp


def create_model(instance):
    """Set card game: among the cards on the table, find three that form a set.
    For each of the four features (number, fill, colour, shape), the three cards
    must show it all the same or all different."""
    cards = instance["cards_data"]  # cards[c] is [number, fill, colour, shape] of card c
    # the values each feature can take, in the order of the columns of a card
    feature_values = [instance["numbers"], instance["fills"],
                      instance["colors"], instance["shapes"]]
    n_cards = len(cards)  # the number of cards on the table

    # No objective: any set on the table is an answer.
    problem = pulp.LpProblem("set_game", pulp.LpMinimize)

    # choose[k][c] is 1 when card c is the k-th card of the set.
    choose = pulp.LpVariable.dicts("choose", (range(3), range(n_cards)), cat="Binary")

    # winning_cards[k] is the index of the k-th card of the set.
    winning_cards = [pulp.LpVariable(f"winning_{k}", 0, n_cards - 1, cat="Integer")
                     for k in range(3)]

    # Each place of the set holds one card, and winning_cards[k] is its index.
    for k in range(3):
        problem += pulp.lpSum(choose[k][c] for c in range(n_cards)) == 1
        problem += winning_cards[k] == pulp.lpSum(c * choose[k][c] for c in range(n_cards))

    # No card is in the set twice.
    for c in range(n_cards):
        problem += pulp.lpSum(choose[k][c] for k in range(3)) <= 1

    # For each feature and value, the three cards show the value on 0, 1 or 3 cards, never 2:
    # all three share the value, or the three values all differ.
    for f, values in enumerate(feature_values):
        for v in values:
            # the cards of the set that show value v for feature f
            shown = pulp.lpSum(choose[k][c] for k in range(3) for c in range(n_cards)
                               if cards[c][f] == v)
            # one_card is 1 when exactly one of the three cards shows value v
            one_card = pulp.LpVariable(f"one_card_{f}_{v}", cat="Binary")
            # all_cards is 1 when all three cards show value v
            all_cards = pulp.LpVariable(f"all_cards_{f}_{v}", cat="Binary")
            problem += shown == one_card + 3 * all_cards
            problem += one_card + all_cards <= 1

    return problem, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

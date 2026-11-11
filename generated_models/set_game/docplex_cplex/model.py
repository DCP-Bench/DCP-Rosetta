# set_game: a CPLEX (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python set_game.py set_game.json

from docplex.mp.model import Model


def create_model(instance):
    """Set card game: among the cards on the table, find three different cards that form a set, meaning
    that for each feature (number, shading, color, shape) the three cards show either all the same value
    or all different values."""
    cards = instance["cards_data"]  # cards[i]: card i, written as [number, shading, color, shape]
    n_cards = len(cards)
    n_features = len(cards[0])  # the number of features of a card
    slots = range(3)

    model = Model("set_game")

    # pick[k, i] = 1 when the k-th winning card is card i; every slot holds exactly one card.
    pick = {(k, i): model.binary_var(name=f"pick_{k}_{i}") for k in slots for i in range(n_cards)}
    model.add_constraints(model.sum(pick[k, i] for i in range(n_cards)) == 1 for k in slots)

    # The three winning cards are different cards.
    model.add_constraints(model.sum(pick[k, i] for k in slots) <= 1 for i in range(n_cards))

    # For every feature, the three cards show all the same value or all different values. With
    # three cards that is: no value of the feature appears on exactly two of them, i.e. each
    # value appears on 0, 1 or 3 cards. For each value, once is 1 when it appears on one card
    # and thrice is 1 when it appears on all three (both 0 when it does not appear).
    for f in range(n_features):
        for v in sorted({card[f] for card in cards}):
            showing = model.sum(pick[k, i] for k in slots for i in range(n_cards) if cards[i][f] == v)
            once = model.binary_var(name=f"once_{f}_{v}")
            thrice = model.binary_var(name=f"thrice_{f}_{v}")
            model.add_constraint(once + thrice <= 1)
            model.add_constraint(showing == once + 3 * thrice)

    # winning_cards[k] is the 0-based index of the k-th card of the set.
    winning_cards = [model.sum(i * pick[k, i] for i in range(n_cards)) for k in slots]
    return model, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)

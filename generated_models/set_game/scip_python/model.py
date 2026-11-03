# set_game: a SCIP (Python) model from DCP Rosetta.
# Download the `set_game.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/set_game.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python set_game.py set_game.json


from pyscipopt import Model, quicksum


def create_model(instance):
    """Set (the card game): find three of the cards on the table that form a set.

    A set is three cards on which each of the four features (number, fill, color,
    shape) is either the same on all three cards or different on all three.
    The output is the 0-based indices of the three cards.
    """
    # cards[c] = [number, fill, color, shape] of card c; each entry is the version
    # of that feature the card shows (a number code, one per version).
    cards = instance["cards_data"]
    n = len(cards)  # the number of cards on the table

    model = Model("set_game")

    # slot[k, c] is 1 when card c is the k-th of the three cards of the set. The
    # problem does not fix an order for the three cards, so none is imposed.
    slot = model.addMatrixVar((3, n), vtype="B", name="slot")

    # Each of the three slots holds exactly one card.
    model.addMatrixCons(slot.sum(axis=1) == 1)

    # Each card fills at most one slot, so the three cards are distinct.
    model.addMatrixCons(slot.sum(axis=0) <= 1)

    # chosen[c] is 1 when card c is one of the three cards of the set.
    chosen = slot.sum(axis=0)

    # For each feature f and each version v shown by some card, the number of
    # chosen cards showing v is 0, 1 or 3, never 2. A count of 2 is two cards that
    # share the version while the third differs, the one pattern the rule forbids;
    # 3 is all three the same, and 0 and 1 are the cases where they all differ.
    for f in range(4):
        for v in sorted({card[f] for card in cards}):
            shows = [c for c in range(n) if cards[c][f] == v]
            count = quicksum(chosen[c] for c in shows)

            # SCIP has no "!=", so "count != 2" is written as "count <= 1 or count >= 3",
            # with a binary low choosing the side: low is 1 when at most one chosen card
            # shows version v of feature f. Exactly three cards are chosen, so count
            # never exceeds 3, and the two sides together allow exactly 0, 1 and 3.
            low = model.addVar(f"low_{f}_{v}", vtype="B")
            model.addConsIndicator(count <= 1, binvar=low)
            model.addConsIndicator(count >= 3, binvar=low, activeone=False)

    # The index of the card in each slot: the sum of c over the cards that can sit
    # there. Each slot holds exactly one card, so the sum is that card's index.
    winning_cards = [quicksum(c * slot[k, c] for c in range(n)) for k in range(3)]

    # A satisfaction problem: the model has no objective.
    return model, {"winning_cards": winning_cards}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

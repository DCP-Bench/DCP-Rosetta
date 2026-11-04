# frog_circle: an Exact (Python) model from DCP Rosetta.
# Download the `frog_circle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/frog_circle.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python frog_circle.py frog_circle.json

from exact import Exact


def create_model(instance):
    """Cards numbered 1 to n lie in a circle. The frog starts on card 1 and, from each card,
    jumps clockwise as many places as the card's number. Find an arrangement of the cards
    from which the frog lands on every card."""
    n_cards = instance["n"]  # the number of cards, numbered 1 to n_cards

    solver = Exact()

    # Exact identifies its variables by name.
    # card_at[p][v] is 1 when card v lies at position p of the circle. The positions run
    # clockwise from 0 to n_cards - 1.
    card_at = [{v: f"position_{p}_holds_{v}" for v in range(1, n_cards + 1)} for p in range(n_cards)]
    for p in range(n_cards):
        for name in card_at[p].values():
            solver.addVariable(name, 0, 1)
        # Each position holds exactly one card.
        solver.addConstraint([(1, name) for name in card_at[p].values()], True, 1, True, 1)
    for v in range(1, n_cards + 1):
        # Each card lies at exactly one position.
        solver.addConstraint([(1, card_at[p][v]) for p in range(n_cards)], True, 1, True, 1)

    # x[p] is the number of the card at position p.
    x = [f"x_{p}" for p in range(n_cards)]
    for p in range(n_cards):
        solver.addVariable(x[p], 1, n_cards)
        # x[p] is the number on the card at position p.
        solver.addConstraint([(v, card_at[p][v]) for v in range(1, n_cards + 1)] + [(-1, x[p])],
                             True, 0, True, 0)

    # The frog starts on card 1, which lies at position 0.
    solver.addConstraint([(1, card_at[0][1])], True, 1, True, 1)

    # at_step[i][p] is 1 when the frog stands on position p after i jumps.
    at_step = [[f"step_{i}_at_position_{p}" for p in range(n_cards)] for i in range(n_cards)]
    for i in range(n_cards):
        for name in at_step[i]:
            solver.addVariable(name, 0, 1)
        # After each number of jumps the frog stands on exactly one position.
        solver.addConstraint([(1, name) for name in at_step[i]], True, 1, True, 1)
    # The frog starts at position 0.
    solver.addConstraint([(1, at_step[0][0])], True, 1, True, 1)
    # The frog stands on each position after exactly one of the n_cards jumps, so it lands on every card.
    for p in range(n_cards):
        solver.addConstraint([(1, at_step[i][p]) for i in range(n_cards)], True, 1, True, 1)

    # Each jump moves the frog clockwise by the number on the card it leaves: from position p
    # holding card v, the next position is (p + v) mod n_cards.
    for i in range(n_cards - 1):
        for p in range(n_cards):
            for v in range(1, n_cards + 1):
                solver.addConstraint([(-1, at_step[i][p]), (-1, card_at[p][v]),
                                      (1, at_step[i + 1][(p + v) % n_cards])], True, -1)

    return solver, {"x": x}


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

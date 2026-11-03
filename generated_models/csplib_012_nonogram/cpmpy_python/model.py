# csplib_012_nonogram: a CPMpy model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

import cpmpy as cp


def line_automaton(rule):
    """Automaton that accepts exactly the lines (0 = empty, 1 = shaded) matching a rule.

    The state counts how much of the rule has been read: inside a block it advances by
    one per shaded cell, and after a block one empty cell is required before the next.
    Returns (transitions, accepting states); the start state is 0.
    """
    blocks = [length for length in rule if length > 0]  # zeros are padding, not blocks
    transitions = []
    state = 0
    for length in blocks:
        transitions.append((state, 0, state))          # empty cells before the block
        for _ in range(length):
            transitions.append((state, 1, state + 1))  # one more shaded cell of the block
            state += 1
        transitions.append((state, 0, state + 1))      # the empty cell that ends the block
        state += 1
    transitions.append((state, 0, state))              # empty cells after the last block
    # The line may end right after the last block or after the empty cells following it.
    # With no blocks there is no state before the last block, so only state 0 accepts.
    accepting = [s for s in (state - 1, state) if s >= 0]
    return transitions, accepting


def create_model(instance):
    """Shade squares in a grid so that in every row and column the blocks of consecutive
    shaded squares have the lengths given by its rule, in order, with at least one
    unshaded square between blocks."""
    row_rules = instance["row_rules"]  # row_rules[r]: the block lengths of row r, in order (0 is padding)
    col_rules = instance["col_rules"]  # col_rules[c]: the block lengths of column c, in order (0 is padding)
    n_rows, n_cols = len(row_rules), len(col_rules)

    # board[r, c] is 1 when the square in row r and column c is shaded, 0 when it is not
    board = cp.intvar(0, 1, shape=(n_rows, n_cols), name="board")

    model = cp.Model()
    # Each row shows the shaded blocks its rule lists, in that order.
    for r, rule in enumerate(row_rules):
        transitions, accepting = line_automaton(rule)
        model.add(cp.Regular(board[r, :], transitions, 0, accepting))

    # Each column shows the shaded blocks its rule lists, in that order.
    for c, rule in enumerate(col_rules):
        transitions, accepting = line_automaton(rule)
        model.add(cp.Regular(board[:, c], transitions, 0, accepting))

    return model, {"board": board}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

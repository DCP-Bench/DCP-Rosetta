# csplib_012_nonogram: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from ortools.sat.python import cp_model


def line_automaton(rule):
    """Automaton that accepts exactly the lines of squares that show the blocks of a rule.

    The state counts how much of the rule has been read: inside a block it advances by
    one per shaded square, and after a block one empty square is required before the next.
    Returns the transitions and the accepting states; the start state is 0.
    """
    blocks = [length for length in rule if length > 0]  # the block lengths of the rule
    transitions = []  # (state, square, next state) steps through the line
    state = 0         # how much of the rule has been read
    for length in blocks:
        transitions.append((state, 0, state))          # empty squares before the block
        for _ in range(length):
            transitions.append((state, 1, state + 1))  # one more shaded square of the block
            state += 1
        transitions.append((state, 0, state + 1))      # the empty square that ends the block
        state += 1
    transitions.append((state, 0, state))              # empty squares after the last block
    # The line may end right after the last block, with or without the empty square after it.
    # With no blocks, only the start state accepts.
    accepting = [s for s in (state - 1, state) if s >= 0]
    return transitions, accepting


def create_model(instance):
    """Shade squares in a grid so that in every row and column the blocks of consecutive
    shaded squares have the lengths given by its rule, in order, with at least one
    unshaded square between blocks."""
    n_rows = instance["rows"]          # the number of rows
    n_cols = instance["cols"]          # the number of columns
    row_rules = instance["row_rules"]  # row_rules[r]: the block lengths of row r, in order
    col_rules = instance["col_rules"]  # col_rules[c]: the block lengths of column c, in order

    model = cp_model.CpModel()

    # board[r][c] is 1 when the square in row r and column c is shaded, 0 when it is empty
    board = [[model.new_int_var(0, 1, f"board_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    # Each row shows the blocks its rule lists, in that order.
    for r, rule in enumerate(row_rules):
        transitions, accepting = line_automaton(rule)
        model.add_automaton(board[r], 0, accepting, transitions)
    # Each column shows the blocks its rule lists, in that order.
    for c, rule in enumerate(col_rules):
        transitions, accepting = line_automaton(rule)
        model.add_automaton([board[r][c] for r in range(n_rows)], 0, accepting, transitions)

    return model, {"board": board}


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

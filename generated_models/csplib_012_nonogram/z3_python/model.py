# csplib_012_nonogram: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

import z3


# The rules for one line of squares: its shaded blocks must match the rule, in order.
# name keeps the start variables of different lines apart.
def line_constraints(cells, rule, name):
    # Zeros in a rule are padding, so only the positive entries are blocks.
    blocks = [b for b in rule if b > 0]
    length = len(cells)
    # starts[j] is the first square of block j.
    starts = [z3.Int(f"{name}_start_{j}") for j in range(len(blocks))]

    constraints = []
    for j, b in enumerate(blocks):
        # Block j lies inside the line.
        constraints += [starts[j] >= 0, starts[j] + b <= length]
        if j > 0:
            # Block j starts after block j - 1 ends, with at least one empty square between them.
            constraints.append(starts[j] >= starts[j - 1] + blocks[j - 1] + 1)
    for i, cell in enumerate(cells):
        # A square is shaded exactly when it lies inside one of the blocks.
        inside = [z3.And(starts[j] <= i, i < starts[j] + b) for j, b in enumerate(blocks)]
        constraints.append((cell == 1) == (z3.Or(inside) if inside else z3.BoolVal(False)))
    return constraints


def create_model(instance):
    """Shade squares in a grid so that in every row and column the blocks of consecutive
    shaded squares have the lengths given by its rule, in order, with at least one
    unshaded square between blocks."""
    n_rows = instance["rows"]          # the number of rows
    n_cols = instance["cols"]          # the number of columns
    row_rules = instance["row_rules"]  # row_rules[r]: block lengths of row r, in order, padded with zeros to row_rule_len entries
    col_rules = instance["col_rules"]  # col_rules[c]: block lengths of column c, in order, padded with zeros to col_rule_len entries

    # board[r][c] is 1 when the square in row r and column c is shaded, 0 when it is not.
    board = [[z3.Int(f"board_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    # The rules of the puzzle.
    solver = z3.Solver()

    # Each square is either shaded (1) or not (0).
    for r in range(n_rows):
        for c in range(n_cols):
            solver.add(board[r][c] >= 0, board[r][c] <= 1)

    # Every row shows its blocks in the order and lengths of its rule.
    for r in range(n_rows):
        solver.add(line_constraints(board[r], row_rules[r], f"row{r}"))

    # Every column shows its blocks in the order and lengths of its rule.
    for c in range(n_cols):
        solver.add(line_constraints([board[r][c] for r in range(n_rows)], col_rules[c], f"col{c}"))

    return solver, {"board": board}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

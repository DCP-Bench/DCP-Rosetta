# csplib_012_nonogram: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

import cvc5.pythonic as c5


def _or(terms):
    # a square covered by one block only
    return terms[0] if len(terms) == 1 else c5.Or(terms)


def shows_blocks(cells, clue, tag):
    """Constraints saying that the squares in `cells` show the blocks of `clue`, in order,
    with at least one empty square between two blocks."""
    lengths = [length for length in clue if length > 0]  # the block lengths; zeros are padding
    n = len(cells)
    if not lengths:
        return [c5.Not(cell) for cell in cells]  # no blocks: every square is empty

    # starts[k] is the first square of block k
    starts = [c5.Int(f"start_{tag}_{k}") for k in range(len(lengths))]
    constraints = []
    # Each block lies inside the line.
    for start, length in zip(starts, lengths):
        constraints += [start >= 0, start + length <= n]
    # Each block starts after the previous block ends, with one empty square in between.
    for k in range(len(lengths) - 1):
        constraints.append(starts[k + 1] >= starts[k] + lengths[k] + 1)
    # A square is shaded exactly when some block covers it.
    for j, cell in enumerate(cells):
        # covered[k] is true when block k covers square j
        covered = [c5.And(starts[k] <= j, j < starts[k] + lengths[k]) for k in range(len(lengths))]
        constraints.append(cell == _or(covered))
    return constraints


def create_model(instance):
    """Shade squares in a grid so that in every row and column the blocks of consecutive
    shaded squares have the lengths given by its rule, in order, with at least one
    unshaded square between blocks."""
    n_rows = instance["rows"]          # the number of rows
    n_cols = instance["cols"]          # the number of columns
    row_rules = instance["row_rules"]  # row_rules[r]: the block lengths of row r, in order, padded with 0
    col_rules = instance["col_rules"]  # col_rules[c]: the block lengths of column c, in order, padded with 0

    # shaded[r][c] is true when the square in row r and column c is shaded
    shaded = [[c5.Bool(f"shaded_{r}_{c}") for c in range(n_cols)] for r in range(n_rows)]

    solver = c5.Solver()

    # Each row shows the blocks of its clue.
    for r in range(n_rows):
        solver.add(shows_blocks(shaded[r], row_rules[r], f"row_{r}"))
    # Each column shows the blocks of its clue.
    for c in range(n_cols):
        solver.add(shows_blocks([shaded[r][c] for r in range(n_rows)], col_rules[c], f"col_{c}"))

    # board[r][c] is 1 for a shaded square and 0 for an empty one
    board = [[c5.If(shaded[r][c], 1, 0) for c in range(n_cols)] for r in range(n_rows)]
    return solver, {"board": board}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

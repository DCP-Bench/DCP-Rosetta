# csplib_012_nonogram: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from exact import Exact


def create_model(instance):
    """Shade squares in a grid so that, in every row and every column, the blocks of consecutive
    shaded squares have the lengths given by that line's rule, in order, with at least one
    unshaded square between blocks."""
    n_rows = instance["rows"]          # number of rows
    n_cols = instance["cols"]          # number of columns
    row_rules = instance["row_rules"]  # row_rules[r]: block lengths of row r, in order; 0 entries are padding
    col_rules = instance["col_rules"]  # col_rules[c]: block lengths of column c, in order; 0 entries are padding

    solver = Exact()

    # Exact identifies its variables by name.
    # board[r][c] is 1 when the square in row r and column c is shaded, and 0 when it is not.
    board = [[f"board_{r}_{c}" for c in range(n_cols)] for r in range(n_rows)]
    for r in range(n_rows):
        for c in range(n_cols):
            solver.addVariable(board[r][c], 0, 1)

    def post_rule(label, cells, rule):
        """The shaded squares among cells form the blocks of rule, in order."""
        blocks = [b for b in rule if b > 0]  # block lengths, without the padding
        if not blocks:
            # An empty rule means no square of the line is shaded.
            solver.addConstraint([(1, cell) for cell in cells], True, 0, True, 0)
            return
        n_cells = len(cells)
        # Number of places the blocks can be shifted, from their packed positions.
        slack = n_cells - (sum(blocks) + len(blocks) - 1)
        # earliest[j] is the first square block j can start on, with the blocks before it packed to the left.
        earliest = []
        position = 0
        for b in blocks:
            earliest.append(position)
            position += b + 1  # the block, and the empty square after it

        # starts[j][k] is 1 when block j starts k squares after its earliest square.
        starts = [[f"{label}_block_{j}_offset_{k}" for k in range(slack + 1)]
                  for j in range(len(blocks))]
        for j in range(len(blocks)):
            for name in starts[j]:
                solver.addVariable(name, 0, 1)
            # Each block starts at exactly one place.
            solver.addConstraint([(1, name) for name in starts[j]], True, 1, True, 1)

        # Blocks keep their order: a block does not start before the one before it. The empty
        # squares between blocks are already in earliest. With no slack the blocks are packed,
        # so their order holds already.
        for j in range(len(blocks) - 1 if slack > 0 else 0):
            solver.addConstraint([(k, starts[j + 1][k]) for k in range(1, slack + 1)]
                                 + [(-k, starts[j][k]) for k in range(1, slack + 1)], True, 0)

        # A square is shaded exactly when some block covers it. A block of length b that starts
        # on square s covers squares s to s + b - 1.
        for i in range(n_cells):
            covering = []  # the block starts that cover square i
            for j, b in enumerate(blocks):
                for k in range(slack + 1):
                    start = earliest[j] + k
                    if start <= i <= start + b - 1:
                        covering.append(starts[j][k])
            solver.addConstraint([(1, cells[i])] + [(-1, name) for name in covering], True, 0, True, 0)

    # The blocks of each row follow the row's rule.
    for r in range(n_rows):
        post_rule(f"row_{r}", board[r], row_rules[r])
    # The blocks of each column follow the column's rule.
    for c in range(n_cols):
        post_rule(f"col_{c}", [board[r][c] for r in range(n_rows)], col_rules[c])

    return solver, {"board": board}


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

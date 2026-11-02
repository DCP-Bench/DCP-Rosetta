# csplib_012_nonogram: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

import pulp


def post_clue(problem, cells, clue, name):
    """Shade the squares of one line so that its shaded blocks have the lengths of the clue,
    in order, with at least one unshaded square between two blocks."""
    blocks = [length for length in clue if length > 0]  # the block lengths; zeros are padding
    size = len(cells)
    if not blocks:
        # An empty clue means no square of the line is shaded.
        for cell in cells:
            problem += cell == 0
        return

    # earliest[k] is the first square where block k can start: the earlier blocks sit at the
    # start of the line, each followed by one unshaded square. latest[k] is the last square where
    # block k can start: the later blocks sit at the end of the line, each preceded by one
    # unshaded square.
    earliest, latest = [], []
    used = 0
    for length in blocks:
        earliest.append(used)
        used += length + 1
    used = 0
    for length in reversed(blocks):
        latest.append(size - used - length)
        used += length + 1
    latest.reverse()

    # begun[k][p] is 1 when block k has started at or before square p. Outside the range from
    # earliest[k] to latest[k] this is already known.
    begun = [{p: pulp.LpVariable(f"{name}_b{k}_{p}", cat="Binary")
              for p in range(earliest[k], latest[k])} for k in range(len(blocks))]

    # Whether block k has started at or before square position: never before its earliest start,
    # always from its latest start on.
    def started_by(k, position):
        if position < earliest[k]:
            return 0
        if position >= latest[k]:
            return 1
        return begun[k][position]

    # Once block k has started, it stays started.
    for k in range(len(blocks)):
        for p in range(earliest[k], latest[k] - 1):
            problem += begun[k][p] <= begun[k][p + 1]

    # Block k+1 starts after block k has ended and one unshaded square follows it. So if block k+1
    # has started by square p, block k had started by square p minus its length minus one.
    for k in range(len(blocks) - 1):
        for p in range(earliest[k + 1], latest[k + 1]):
            problem += begun[k + 1][p] <= started_by(k, p - blocks[k] - 1)

    # A square is shaded exactly when some block covers it. Block k covers square c when it has
    # started by c but not by c minus its length.
    for c in range(size):
        problem += cells[c] == pulp.lpSum(
            started_by(k, c) - started_by(k, c - blocks[k]) for k in range(len(blocks)))


def create_model(instance):
    """Shade the squares of a grid so that every row and every column shows its clue: the
    lengths of its blocks of consecutive shaded squares, in order."""
    n_rows = instance["rows"]          # the number of rows
    n_cols = instance["cols"]          # the number of columns
    row_rules = instance["row_rules"]  # row_rules[r]: the clue of row r
    col_rules = instance["col_rules"]  # col_rules[c]: the clue of column c

    problem = pulp.LpProblem("nonogram", pulp.LpMinimize)

    # board[r][c] is 1 when the square in row r and column c is shaded, 0 when it is empty.
    board = [[pulp.LpVariable(f"board_{r}_{c}", cat="Binary") for c in range(n_cols)]
             for r in range(n_rows)]

    # Each row shows its clue.
    for r in range(n_rows):
        post_clue(problem, board[r], row_rules[r], f"row{r}")

    # Each column shows its clue.
    for c in range(n_cols):
        post_clue(problem, [board[r][c] for r in range(n_rows)], col_rules[c], f"col{c}")

    return problem, {"board": board}


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

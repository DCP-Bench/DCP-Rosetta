# csplib_012_nonogram: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def add_line(cnf, pool, cells, rule, key):
    """Require the squares of one line, read from one end to the other, to show the blocks of
    rule in order, with at least one unshaded square between two blocks. Zero entries of the
    rule are padding and are not blocks.

    Reading the squares, the line is in one stage at a time: before the first block, inside a
    block after some of its shaded squares, or in the gap after a block. The stage after each
    square follows from the squares read so far. The line may end just after the last block or
    after the unshaded squares that follow it."""
    blocks = [length for length in rule if length > 0]
    n = len(cells)

    # next_stage[(stage, bit)]: the stage after reading a square, bit 1 when it is shaded.
    # Stage 0 is the gap before the first block.
    next_stage = {}
    stage = 0
    for length in blocks:
        next_stage[(stage, 0)] = stage            # unshaded squares before the block
        for _ in range(length):
            next_stage[(stage, 1)] = stage + 1    # one more shaded square of the block
            stage += 1
        next_stage[(stage, 0)] = stage + 1        # the block is full, so an unshaded square follows
        stage += 1
    next_stage[(stage, 0)] = stage                # unshaded squares after the last block
    # stages in which the line may end
    accepting = {stage - 1, stage} if blocks else {stage}

    # reachable[i]: stages the line can be in after i squares. can_finish[i]: those of them from
    # which the line can still end in an accepting stage. Only these stages are kept.
    reachable = [{0}]
    for _ in range(n):
        reachable.append({next_stage[(s, b)] for s in reachable[-1] for b in (0, 1)
                          if (s, b) in next_stage})
    can_finish = [set() for _ in range(n + 1)]
    can_finish[n] = reachable[n] & accepting
    for i in range(n - 1, -1, -1):
        can_finish[i] = {s for s in reachable[i]
                         if any(next_stage.get((s, b)) in can_finish[i + 1] for b in (0, 1))}
    if 0 not in can_finish[0]:
        # The blocks cannot fit in this line, so no square pattern works.
        cnf.append([])
        return

    # in_stage[i][s]: the line is in stage s after i squares
    in_stage = [{s: pool.id((key, i, s)) for s in can_finish[i]} for i in range(n + 1)]
    cnf.append([in_stage[0][0]])                  # the line starts in the gap before the first block
    for i in range(n):
        for target, now in in_stage[i + 1].items():
            sources = [(s, b) for s in can_finish[i] for b in (0, 1)
                       if next_stage.get((s, b)) == target]
            bit = sources[0][1]                   # every stage reached from another reads the same square
            square = cells[i] if bit == 1 else -cells[i]
            # The line reaches the stage only through the square that leads there, from a stage that leads there.
            cnf.append([-now, square])
            cnf.append([-now] + [in_stage[i][s] for s, _ in sources])
            for s, _ in sources:
                cnf.append([-in_stage[i][s], -square, now])
    for i in range(1, n + 1):
        cnf.append(list(in_stage[i].values()))    # each square leaves the line in a stage that can still finish


def create_model(instance):
    """Shade squares in a grid so that in every row and column the blocks of consecutive shaded
    squares have the lengths given by its rule, in order, with at least one unshaded square
    between two blocks."""
    n_rows = instance["rows"]          # the number of rows in the grid
    n_cols = instance["cols"]          # the number of columns in the grid
    # row_rule_len and col_rule_len: how many entries each rule lists. Shorter rules are padded with zeros.
    row_rules = instance["row_rules"]  # row_rules[r]: the block lengths of row r, in order
    col_rules = instance["col_rules"]  # col_rules[c]: the block lengths of column c, in order

    pool = IDPool()

    # board[r][c]: 1 when the square in row r and column c is shaded, 0 when it is not
    board = [[Integer(f"board{r}_{c}", 0, 1, vpool=pool) for c in range(n_cols)]
             for r in range(n_rows)]
    engine = IntegerEngine(vars=[cell for row in board for cell in row], vpool=pool)
    cnf = engine.clausify()
    # shaded[r][c]: the square in row r and column c is shaded
    shaded = [[board[r][c].equals(1) for c in range(n_cols)] for r in range(n_rows)]

    # Each row shows the shaded blocks its rule lists, in that order.
    for r in range(n_rows):
        add_line(cnf, pool, shaded[r], row_rules[r], ("row", r))
    # Each column shows the shaded blocks its rule lists, in that order.
    for c in range(n_cols):
        add_line(cnf, pool, [shaded[r][c] for r in range(n_rows)], col_rules[c], ("col", c))

    return cnf, {"board": board}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

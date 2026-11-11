# csplib_012_nonogram: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_012_nonogram.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_012_nonogram.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_012_nonogram.py csplib_012_nonogram.json

from pycsp3 import *


def create_model(instance):
    """Nonograms are a popular puzzle. Shade in squares of a grid so that the blocks of consecutive
    shaded squares in each row and each column satisfy the constraints given for that row or column.
    A constraint lists the lengths of the blocks in order, with unspecified gaps between them."""
    n_rows = instance["rows"]   # the number of rows
    n_cols = instance["cols"]   # the number of columns
    # row_rules[r] is the clue of row r: its block lengths from left to right, padded with zeros on the left.
    row_rules = instance["row_rules"]
    # col_rules[c] is the clue of column c, read the same way from top to bottom.
    col_rules = instance["col_rules"]

    def blocks(clue):
        # The block lengths of a clue in order. Zeros only pad the clue on the left to its length, so they
        # are dropped; this is a reading of the padding, not a block of length zero.
        return [length for length in clue if length > 0]

    def line_automaton(block_lengths):
        # Reads one line of 0/1 cells and accepts exactly the lines whose blocks of 1s have these
        # lengths in this order, with at least one 0 between consecutive blocks.
        # State gap<k>: blocks 0 to k-1 are complete and the next cell may be 0 or start block k.
        # State block<k>_<j>: j cells of block k are shaded so far.
        transitions = []
        for k, length in enumerate(block_lengths):
            transitions.append((f"gap{k}", 0, f"gap{k}"))
            transitions.append((f"gap{k}", 1, f"block{k}_1"))
            for j in range(1, length):
                transitions.append((f"block{k}_{j}", 1, f"block{k}_{j + 1}"))
            transitions.append((f"block{k}_{length}", 0, f"gap{k + 1}"))
        n_blocks = len(block_lengths)
        transitions.append((f"gap{n_blocks}", 0, f"gap{n_blocks}"))
        # The line may end in a gap after the last block, or with the last block's final cell.
        final = [f"gap{n_blocks}"]
        if n_blocks > 0:
            final.append(f"block{n_blocks - 1}_{block_lengths[-1]}")
        return Automaton(start="gap0", transitions=transitions, final=final)

    # board[r][c] is 1 when the square in row r and column c is shaded, 0 when it is not.
    board = VarArray(size=[n_rows, n_cols], dom={0, 1})

    satisfy(
        # Each row's shaded blocks follow the row's clue.
        (Regular(scope=board[r], automaton=line_automaton(blocks(row_rules[r])))
         for r in range(n_rows)),

        # Each column's shaded blocks follow the column's clue.
        (Regular(scope=board[:, c], automaton=line_automaton(blocks(col_rules[c])))
         for c in range(n_cols)),
    )

    return {"board": board}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("board", "=")
        for row in outputs["board"]:
            print(values(row))
    else:
        print("No solution:", status())

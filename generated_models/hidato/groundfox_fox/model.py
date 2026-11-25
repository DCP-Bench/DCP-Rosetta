# hidato: a FOX model for GroundFOX from DCP Rosetta.
#
# Hidato Puzzles start semi-filled with numbered tiles. Connect the numbers together to win.
# Consecutive number must touch horizontally, vertically, or diagonally. The numbers must be
# in increasing order. Fill in the empty cells, marked 0 in the given puzzle, with the numbers
# that complete the puzzle, so that the grid holds each number from 1 to the number of cells
# exactly once.
#
# Print the solved puzzle (x) as a list of lists of integers.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hidato.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py hidato.json --check

# hidato: a FOX model for GroundFOX from DCP Rosetta.
#
# Hidato: fill the empty cells (0 in the puzzle) with the numbers 1..R*C, each used once, so
# that consecutive numbers touch horizontally, vertically or diagonally. Print the solved
# puzzle (x) as a list of lists of integers.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

# Cells are also numbered by a flat id p (Cell/1, CellOf(r, c, p), Adj(p, q)) so that every
# existential is a single quantifier: the proof checker does not accept nested existentials.
# x(r, c, v): cell (r, c) holds v (the output). y(p, v): cell p holds v (the working copy).
# Exactly one value per cell and each value somewhere make the assignment a bijection.
# Each value v has a cell touching the cell of v+1.
FOX = """
invocabulary { Row/1 Col/1 Cell/1 Val/1 Lt/2 Succ/2 Adj/2 CellOf/3 Clue/3 }
outvocabulary { x/3 y/2 }
theory {
    ! p [Cell(p)] : ? v [Val(v)] : y(p,v).
    ! p [Cell(p)] : ! v [Val(v)] : ! w [Lt(v,w)] : ~y(p,v) | ~y(p,w).
    ! v [Val(v)] : ? p [Cell(p)] : y(p,v).
    ! r [Row(r)] : ! c [Col(c)] : ! p [CellOf(r,c,p)] : ! v [Val(v)] : ~x(r,c,v) | y(p,v).
    ! r [Row(r)] : ! c [Col(c)] : ! p [CellOf(r,c,p)] : ! v [Val(v)] : ~y(p,v) | x(r,c,v).
    ! r [Row(r)] : ! c [Col(c)] : ! v [Clue(r,c,v)] : x(r,c,v).
    ! v [Val(v)] : ! w [Succ(v,w)] : ! p [Cell(p)] : ? q [Adj(p,q)] : y(q,w) | ~y(p,v).
}
"""


def structure(instance):
    grid = instance["puzzle"]
    rows = len(grid)
    cols = len(grid[0])
    total = rows * cols
    values = list(range(1, total + 1))
    cell_of = [(r, c, r * cols + c) for r in range(rows) for c in range(cols)]
    adj = []
    for r in range(rows):
        for c in range(cols):
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if (dr, dc) == (0, 0):
                        continue
                    r2, c2 = r + dr, c + dc
                    if 0 <= r2 < rows and 0 <= c2 < cols:
                        adj.append((r * cols + c, r2 * cols + c2))
    clues = [(r, c, grid[r][c]) for r in range(rows) for c in range(cols) if grid[r][c] != 0]
    return {
        "domain": list(range(0, total + 1)),
        "Row": list(range(rows)),
        "Col": list(range(cols)),
        "Cell": list(range(total)),
        "Val": values,
        "Lt": [(v, w) for v in values for w in values if v < w],
        "Succ": [(v, v + 1) for v in values if v + 1 <= total],
        "Adj": adj,
        "CellOf": cell_of,
        "Clue": clues,
    }

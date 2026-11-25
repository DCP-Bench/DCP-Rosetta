# sudoku: a FOX model for GroundFOX from DCP Rosetta.
#
# The goal of Sudoku is to fill a 9x9 grid with numbers so that each row, column and 3x3
# section contain all the digits between 1 and 9.
#
# Input is a grid with some cells filled with numbers and some empty.
#
# Print the solved grid (grid) as a list of lists.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/sudoku.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py sudoku.json --check

# sudoku: a FOX model for GroundFOX from DCP Rosetta.
#
# Fill a 9x9 grid with 1..9 so every row, column and 3x3 box holds each digit once.
# The clues come from the instance (a 0 cell is empty); they are data relations.

FOX = """
invocabulary { Cell/1 Dig/1 Clue/3 Peer/4 }
outvocabulary { grid/3 }
theory {
    ! i [Cell(i)] : ! j [Cell(j)] : ? v [Dig(v)] : grid(i, j, v).
    ! i [Cell(i)] : ! j [Cell(j)] : ! v [Dig(v)] : ! w [Dig(w) & v ~= w] : ~grid(i, j, v) | ~grid(i, j, w).
    ! i [Cell(i)] : ! j [Cell(j)] : ! k [Cell(k)] : ! l [Peer(i, j, k, l)] : ! v [Dig(v)] : ~grid(i, j, v) | ~grid(k, l, v).
    ! i [Cell(i)] : ! j [Cell(j)] : ! v [Clue(i, j, v)] : grid(i, j, v).
}
"""


def structure(instance):
    givens = instance["input_grid"]
    cells = list(range(9))
    dig = list(range(1, 10))
    clue = [(i, j, givens[i][j]) for i in cells for j in cells if givens[i][j] != 0]
    peer = []
    for i in cells:
        for j in cells:
            for k in cells:
                for l in cells:
                    if (i, j) == (k, l):
                        continue
                    same_box = (i // 3 == k // 3) and (j // 3 == l // 3)
                    if i == k or j == l or same_box:
                        peer.append((i, j, k, l))
    return {"domain": range(10), "Cell": cells, "Dig": dig, "Clue": clue, "Peer": peer}

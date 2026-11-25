# flow_free_game: a FOX model for GroundFOX from DCP Rosetta.
#
# Connect matching colors with pipe to create a flow. Pair all colors, and cover the entire
# board to solve each puzzle in Flow Free. But watch out, pipes will break if they cross or
# overlap! For this problem instance, we have a 5x5 board with the following configuration:
#
# ```text 1, 0, 0, 2, 3 0, 0, 0, 4, 0 0, 0, 4, 0, 0 0, 2, 3, 0, 5 0, 1, 5, 0, 0 ```
#
# The cells with a value of 0 are empty and need to be filled with a color. Cells are
# connected horizontally and vertically: a numbered cell has exactly one neighbour of its own
# color, and a filled cell has exactly two.
#
# Print the board (B) as a list of lists, where each cell value is the color of the cell as an
# integer from 1 to 5.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/flow_free_game.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py flow_free_game.json --check

# flow_free_game: a FOX model for GroundFOX from DCP Rosetta.
#
# Flow Free on a grid: every cell gets a colour 1..5 (the instance's numbered cells are fixed). A
# numbered cell has exactly one neighbour of its own colour, every other cell exactly two.
# Print the board (B) as a list of lists of colours.
#
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py <instance>.json

FOX = """
invocabulary { Row/1 Colm/1 Col/1 Fix/3 End/2 Mid/2 Up/4 Down/4 Left/4 Right/4 NoUp/2 NoDown/2 NoLeft/2 NoRight/2 }
outvocabulary { B/3 LU/2 LD/2 LL/2 LR/2 }
theory {
    ! r [Row(r)] : ! c [Colm(c)] : ? k [Col(k)] : B(r,c,k).
    ! r [Row(r)] : ! c [Colm(c)] : ! k [Col(k)] : ! j [Col(j) & k ~= j] : ~B(r,c,k) | ~B(r,c,j).
    ! r [Row(r)] : ! c [Colm(c)] : ! k [Fix(r,c,k)] : B(r,c,k).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Up(r,c,r2,c2)] : ! k [Col(k)] : ~B(r,c,k) | ~B(r2,c2,k) | LU(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Up(r,c,r2,c2)] : ! k [Col(k)] : ~LU(r,c) | ~B(r,c,k) | B(r2,c2,k).
    ! r [Row(r)] : ! c [NoUp(r,c)] : ~LU(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Down(r,c,r2,c2)] : ! k [Col(k)] : ~B(r,c,k) | ~B(r2,c2,k) | LD(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Down(r,c,r2,c2)] : ! k [Col(k)] : ~LD(r,c) | ~B(r,c,k) | B(r2,c2,k).
    ! r [Row(r)] : ! c [NoDown(r,c)] : ~LD(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Left(r,c,r2,c2)] : ! k [Col(k)] : ~B(r,c,k) | ~B(r2,c2,k) | LL(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Left(r,c,r2,c2)] : ! k [Col(k)] : ~LL(r,c) | ~B(r,c,k) | B(r2,c2,k).
    ! r [Row(r)] : ! c [NoLeft(r,c)] : ~LL(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Right(r,c,r2,c2)] : ! k [Col(k)] : ~B(r,c,k) | ~B(r2,c2,k) | LR(r,c).
    ! r [Row(r)] : ! c [Colm(c)] : ! r2 : ! c2 [Right(r,c,r2,c2)] : ! k [Col(k)] : ~LR(r,c) | ~B(r,c,k) | B(r2,c2,k).
    ! r [Row(r)] : ! c [NoRight(r,c)] : ~LR(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : LU(r,c) | LD(r,c) | LL(r,c) | LR(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : ~LU(r,c) | ~LD(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : ~LU(r,c) | ~LL(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : ~LU(r,c) | ~LR(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : ~LD(r,c) | ~LL(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : ~LD(r,c) | ~LR(r,c).
    ! r [Row(r)] : ! c [End(r,c)] : ~LL(r,c) | ~LR(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : LU(r,c) | LD(r,c) | LL(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : LU(r,c) | LD(r,c) | LR(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : LU(r,c) | LL(r,c) | LR(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : LD(r,c) | LL(r,c) | LR(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : ~LU(r,c) | ~LD(r,c) | ~LL(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : ~LU(r,c) | ~LD(r,c) | ~LR(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : ~LU(r,c) | ~LL(r,c) | ~LR(r,c).
    ! r [Row(r)] : ! c [Mid(r,c)] : ~LD(r,c) | ~LL(r,c) | ~LR(r,c).
}
"""


def structure(instance):
    board = instance["board"]
    rows = len(board)
    cols = len(board[0])
    colours = max([5] + [v for row in board for v in row])
    cells = [(r, c) for r in range(rows) for c in range(cols)]
    fix = [(r, c, board[r][c]) for (r, c) in cells if board[r][c] != 0]
    end = [(r, c) for (r, c) in cells if board[r][c] != 0]
    mid = [(r, c) for (r, c) in cells if board[r][c] == 0]
    return {
        "Row": list(range(rows)),
        "Colm": list(range(cols)),
        "Col": list(range(1, colours + 1)),
        "Fix": fix,
        "End": end,
        "Mid": mid,
        "Up": [(r, c, r - 1, c) for (r, c) in cells if r > 0],
        "Down": [(r, c, r + 1, c) for (r, c) in cells if r < rows - 1],
        "Left": [(r, c, r, c - 1) for (r, c) in cells if c > 0],
        "Right": [(r, c, r, c + 1) for (r, c) in cells if c < cols - 1],
        "NoUp": [(r, c) for (r, c) in cells if r == 0],
        "NoDown": [(r, c) for (r, c) in cells if r == rows - 1],
        "NoLeft": [(r, c) for (r, c) in cells if c == 0],
        "NoRight": [(r, c) for (r, c) in cells if c == cols - 1],
    }

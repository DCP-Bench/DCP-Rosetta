# minesweeper: a FOX model for GroundFOX from DCP Rosetta.
#
# Minesweeper rules are very simple. The board is divided into cells, with mines randomly
# distributed. To win, you need to open all the cells. The number on a cell shows the number
# of mines adjacent to it. Using this information, you can determine cells that are safe, and
# cells that contain mines. Cells suspected of being mines can be marked with a flag using the
# right mouse button.
#
# The task is to determine which 'X' fields contain mines based on the provided numerical
# clues.
#
# Print whether each cell is a mine or not (mines) as a list of lists of booleans, where True
# indicates a mine and False indicates no mine.
#
# The theory is grounded by GroundFOX into CNF with a CertiFOX proof (checked by checkfox) and
# solved by a SAT solver; structure(instance) supplies the input relations from the data.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/minesweeper.html
# Run (groundfox from https://gitlab.kuleuven.be/krr/software/groundfox-checkfox, pip install python-sat):
#   python dcp_fox.py model.py minesweeper.json --check

# minesweeper: a FOX model for GroundFOX from DCP Rosetta.
#
# mines[i][j] is 1 iff the cell is a mine. Every revealed clue (game_data value other
# than X) fixes the number of mines among its neighbours. Each neighbourhood is a chain
# of nodes; reach(g, s) is the running count through node g, forced forward from the
# mine variables, and the last node of each chain must equal the clue.

FOX = """
invocabulary { Row/1 Col/1 Bit/1 Sum/1 Add/3 Node/1 Start/1 End/1 Nxt/2 NbCell/3 Want/2 Open/2 }
outvocabulary { mines/3 reach/2 }
theory {
    ! i [Row(i)] : ! j [Col(j)] : ? b [Bit(b)] : mines(i, j, b).
    ! i [Row(i)] : ! j [Col(j)] : ! b [Bit(b)] : ! c [Bit(c) & b ~= c] : ~mines(i, j, b) | ~mines(i, j, c).
    ! i [Row(i)] : ! j [Col(j) & Open(i, j)] : ~mines(i, j, 1).
    ! g [Start(g)] : ! i [Row(i)] : ! j [Col(j) & NbCell(g, i, j)] : ! v [Bit(v)] : ~mines(i, j, v) | reach(g, v).
    ! g [Node(g)] : ! h [Nxt(g, h)] : ! i [Row(i)] : ! j [Col(j) & NbCell(h, i, j)] : ! s [Sum(s)] : ! v [Bit(v)] : ! t [Sum(t) & Add(s, v, t)] : ~reach(g, s) | ~mines(i, j, v) | reach(h, t).
    ! g [End(g)] : ! s [Sum(s) & ~Want(g, s)] : ~reach(g, s).
    ! g [End(g)] : ? s [Want(g, s)] : reach(g, s).
}
"""


def structure(instance):
    x_code = instance["X"]
    board = instance["game_data"]
    rows = len(board)
    cols = len(board[0]) if rows else 0
    nb_cell, start, end, nxt, want, open_cells = [], [], [], [], [], []
    for i in range(rows):
        for j in range(cols):
            clue = board[i][j]
            if clue == x_code:
                continue
            open_cells.append((i, j))
            neighbours = [(i + di, j + dj) for di in (-1, 0, 1) for dj in (-1, 0, 1)
                          if (di, dj) != (0, 0)
                          and 0 <= i + di < rows and 0 <= j + dj < cols]
            first = len(nb_cell)
            for pos, (ni, nj) in enumerate(neighbours):
                g = len(nb_cell)
                nb_cell.append((g, ni, nj))
                if pos == 0:
                    start.append(g)
                else:
                    nxt.append((g - 1, g))
            last = len(nb_cell) - 1
            if neighbours:
                end.append(last)
                want.append((last, clue))
    return {
        "Row": list(range(rows)),
        "Col": list(range(cols)),
        "Bit": [0, 1],
        "Sum": list(range(9)),
        "Add": [(s, v, s + v) for s in range(9) for v in (0, 1) if s + v <= 8],
        "Node": list(range(len(nb_cell))),
        "Start": start,
        "End": end,
        "Nxt": nxt,
        "NbCell": nb_cell,
        "Want": [(g, k) for g, k in want if 0 <= k <= 8],
        "Open": open_cells,
    }

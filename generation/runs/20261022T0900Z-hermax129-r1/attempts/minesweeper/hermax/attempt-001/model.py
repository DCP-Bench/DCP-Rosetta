from hermax.model import Model


def build(instance):
    board = instance["game_data"]
    rows = len(board)
    cols = len(board[0])

    m = Model()
    # mines[r][c] is true when the cell holds a mine.
    mines = m.bool_matrix("mine", rows, cols)

    for r in range(rows):
        for c in range(cols):
            clue = board[r][c]
            if clue < 0:
                # Unopened cell: its mine status is what we are solving for.
                continue
            # Opened cells show a number, so they cannot hold a mine.
            m &= (~mines[r][c])
            # The number is the count of mines among the eight neighbours.
            neighbours = [
                mines[a][b]
                for a in range(r - 1, r + 2)
                for b in range(c - 1, c + 2)
                if (a, b) != (r, c) and 0 <= a < rows and 0 <= b < cols
            ]
            m &= (sum(neighbours) == clue)

    return m, {"mines": mines}

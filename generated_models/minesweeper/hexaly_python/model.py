"""Minesweeper: find the mines among the unknown cells so that every number counts its adjacent mines."""
import hexaly.optimizer as hx


def build(instance):
    unknown, game = instance["X"], instance["game_data"]  # game[r][c] is a clue, or `unknown`
    rows, cols = len(game), len(game[0])
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Only unknown cells can hold a mine; a numbered cell is open, so it has none
    mines = [[model.bool() if game[r][c] == unknown else 0 for c in range(cols)] for r in range(rows)]

    # The number on a cell is how many of its (up to eight) neighbours hold a mine
    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unknown:
                around = [mines[i][j] for i in range(r - 1, r + 2) for j in range(c - 1, c + 2)
                          if 0 <= i < rows and 0 <= j < cols and (i, j) != (r, c)]
                model.constraint(model.sum(around) == game[r][c])

    return optimizer, {"mines": mines}

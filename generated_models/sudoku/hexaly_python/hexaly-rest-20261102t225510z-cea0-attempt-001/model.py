"""Sudoku: fill the grid so every row, column and 3 x 3 box holds each digit 1..9 once, keeping the given digits."""
import hexaly.optimizer as hx


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell
    n = len(given)
    box = int(round(n ** 0.5))
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[r][c][v] = 1 if cell (r, c) holds v + 1; Booleans with linear sums
    has = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            model.constraint(model.sum(has[r][c]) == 1)

    # Each row, column and box contains each digit exactly once
    for v in range(n):
        for r in range(n):
            model.constraint(model.sum(has[r][c][v] for c in range(n)) == 1)
        for c in range(n):
            model.constraint(model.sum(has[r][c][v] for r in range(n)) == 1)
        for br in range(0, n, box):
            for bc in range(0, n, box):
                model.constraint(model.sum(has[r][c][v] for r in range(br, br + box) for c in range(bc, bc + box)) == 1)
    # The given digits stay
    for r in range(n):
        for c in range(n):
            if given[r][c]:
                model.constraint(has[r][c][given[r][c] - 1] == 1)

    grid = [[model.sum((v + 1) * has[r][c][v] for v in range(n)) for c in range(n)] for r in range(n)]
    return optimizer, {"grid": grid}

"""Killer sudoku: a sudoku whose cages must add up to their totals, with no number repeated within a cage."""
import hexaly.optimizer as hx


def build(instance):
    n, cages = instance["n"], instance["problem"]  # cages: [total, [[row, col], ...]] with 1-based cells
    box = int(round(n ** 0.5))
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[r][c][v] = 1 if cell (r, c) holds v + 1; Booleans with linear sums
    has = [[[model.bool() for _ in range(n)] for _ in range(n)] for _ in range(n)]
    for r in range(n):
        for c in range(n):
            model.constraint(model.sum(has[r][c]) == 1)

    # Each row, column and nonet contains each number exactly once
    for v in range(n):
        for r in range(n):
            model.constraint(model.sum(has[r][c][v] for c in range(n)) == 1)
        for c in range(n):
            model.constraint(model.sum(has[r][c][v] for r in range(n)) == 1)
        for br in range(0, n, box):
            for bc in range(0, n, box):
                model.constraint(model.sum(has[r][c][v] for r in range(br, br + box) for c in range(bc, bc + box)) == 1)

    x = [[model.sum((v + 1) * has[r][c][v] for v in range(n)) for c in range(n)] for r in range(n)]
    for total, cells in cages:
        cells = [(row - 1, col - 1) for row, col in cells]
        # The numbers in a cage add up to its total
        model.constraint(model.sum(x[r][c] for r, c in cells) == total)
        # No number appears twice in a cage
        for v in range(n):
            model.constraint(model.sum(has[r][c][v] for r, c in cells) <= 1)

    return optimizer, {"x": x}

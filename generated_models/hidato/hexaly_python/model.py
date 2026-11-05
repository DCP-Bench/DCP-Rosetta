"""Hidato: number the grid 1..rows*cols so that consecutive numbers touch, including diagonally, keeping the givens."""
import hexaly.optimizer as hx


def build(instance):
    puzzle = instance["puzzle"]  # 0 marks an empty square
    rows, cols = len(puzzle), len(puzzle[0])
    cells = rows * cols
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # holds[cell][k] = 1 if the square with that index (r * cols + c) holds the number k + 1. Booleans with linear
    # sums let Hexaly treat the whole puzzle as one linear system, which it can also prove things about (that no
    # second solution exists).
    holds = [[model.bool() for _ in range(cells)] for _ in range(cells)]
    for cell in range(cells):
        model.constraint(model.sum(holds[cell]) == 1)   # one number per square
    for k in range(cells):
        model.constraint(model.sum(holds[cell][k] for cell in range(cells)) == 1)   # each number on one square

    # Consecutive numbers touch horizontally, vertically or diagonally: if a square holds k, a neighbour holds k + 1
    for r in range(rows):
        for c in range(cols):
            neighbours = [rr * cols + cc
                          for rr in range(max(r - 1, 0), min(r + 2, rows))
                          for cc in range(max(c - 1, 0), min(c + 2, cols)) if (rr, cc) != (r, c)]
            for k in range(cells - 1):
                model.constraint(holds[r * cols + c][k] <= model.sum(holds[n][k + 1] for n in neighbours))

    # The given numbers stay where they are
    for r in range(rows):
        for c in range(cols):
            if puzzle[r][c]:
                model.constraint(holds[r * cols + c][puzzle[r][c] - 1] == 1)

    # The number on each square
    x = [[model.sum((k + 1) * holds[r * cols + c][k] for k in range(cells)) for c in range(cols)] for r in range(rows)]
    return optimizer, {"x": x}

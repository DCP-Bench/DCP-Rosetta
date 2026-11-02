"""Hidato: number the grid 1..rows*cols so that consecutive numbers touch, including diagonally, keeping the givens."""
import hexaly.optimizer as hx


def build(instance):
    puzzle = instance["puzzle"]  # 0 marks an empty square
    rows, cols = len(puzzle), len(puzzle[0])
    cells = rows * cols
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The path visits every square once: path[t] is the square (r * cols + c) holding number t + 1
    path = model.list(cells)
    model.constraint(model.count(path) == cells)

    # Consecutive numbers touch horizontally, vertically or diagonally
    for t in range(cells - 1):
        a, b = path[t], path[t + 1]
        model.constraint(model.abs(a // cols - b // cols) <= 1)
        model.constraint(model.abs(a % cols - b % cols) <= 1)
    # The given numbers stay where they are
    for r in range(rows):
        for c in range(cols):
            if puzzle[r][c]:
                model.constraint(path[puzzle[r][c] - 1] == r * cols + c)

    # The number on each square: its place on the path, from 1
    x = [[model.index(path, r * cols + c) + 1 for c in range(cols)] for r in range(rows)]
    return optimizer, {"x": x}

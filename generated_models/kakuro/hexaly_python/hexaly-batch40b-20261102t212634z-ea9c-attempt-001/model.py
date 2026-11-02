"""Kakuro: digits 1..9 in the white cells so that every entry adds up to its clue with no digit repeated."""
import hexaly.optimizer as hx


def build(instance):
    n, entries, blanks = instance["n"], instance["problem"], instance["blanks"]  # cells are 1-based [row, col]
    black = {(r - 1, c - 1) for r, c in blanks}
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # has[r][c][v] = 1 if white cell (r, c) holds digit v + 1; Booleans with linear sums
    has = {}
    for r in range(n):
        for c in range(n):
            if (r, c) not in black:
                has[r, c] = [model.bool() for _ in range(9)]
                model.constraint(model.sum(has[r, c]) == 1)
    # A blank cell shows 0, a white cell its digit
    x = [[0 if (r, c) in black else model.sum((v + 1) * has[r, c][v] for v in range(9)) for c in range(n)]
         for r in range(n)]

    for entry in entries:
        clue, cells = entry[0], [(r - 1, c - 1) for r, c in entry[1:]]
        # The digits of an entry add up to its clue
        model.constraint(model.sum(x[r][c] for r, c in cells) == clue)
        # No digit is repeated within an entry
        for v in range(9):
            model.constraint(model.sum(has[r, c][v] for r, c in cells) <= 1)

    return optimizer, {"x": x}

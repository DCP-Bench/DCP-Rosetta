"""Crossfigures: fill a numeric crossword so that every across and down entry satisfies its clue."""
import hexaly.optimizer as hx

# The grid of the problem statement: X is a black cell, a number labels the first cell of an entry
GRID = """
1  2  _  3  X  4  _  5  6
7  _  X  8  _  _  X  9  _
_  X  10 _  X  11 12 X  _
13 14 _  _  X  15 _  16 _
X  _  X  X  X  X  X  _  X
17 _  18 19 X  20 21 _  22
_  X  23 _  X  24 _  X  _
25 26 X  27 _  _  X  28 _
29 _  _  _  X  30 _  _  _
"""


def build(instance):
    rows = [line.split() for line in GRID.strip().splitlines()]
    height, width = len(rows), len(rows[0])
    white = [[token != "X" for token in row] for row in rows]
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # digit[r][c] is the digit in a white cell; black cells show 0
    digit = [[model.int(0, 9) if white[r][c] else 0 for c in range(width)] for r in range(height)]

    # Each entry (direction 'A' across or 'D' down, label) is a number read off its run of white cells
    entry = {}
    for r in range(height):
        for c in range(width):
            if not white[r][c] or not rows[r][c].isdigit():
                continue
            label = int(rows[r][c])
            for direction, dr, dc in (("A", 0, 1), ("D", 1, 0)):
                starts = r - dr < 0 or c - dc < 0 or not white[r - dr][c - dc]
                cells = []
                i, j = r, c
                while i < height and j < width and white[i][j]:
                    cells.append(digit[i][j])
                    i, j = i + dr, j + dc
                if starts and len(cells) > 1:
                    value = model.int(10 ** (len(cells) - 1), 10 ** len(cells) - 1)  # the number the entry spells, with no leading zero
                    model.constraint(value == model.sum(10 ** (len(cells) - 1 - k) * cells[k] for k in range(len(cells))))
                    entry[direction, label] = value

    def A(n):
        return entry["A", n]

    def D(n):
        return entry["D", n]

    clues = [
        A(1) == 2 * A(27),            # 27 across times two
        A(4) == D(4) + 71,            # 4 down plus seventy-one
        A(7) == D(18) + 4,            # 18 down plus four
        16 * A(8) == D(6),            # 6 down divided by sixteen
        A(9) == D(2) - 18,            # 2 down minus eighteen
        A(10) == 72,                  # a dozen in six gross: 864 / 12
        A(11) == D(5) - 70,           # 5 down minus seventy
        A(13) == D(26) * A(23),       # 26 down times 23 across
        A(15) == D(6) - 350,          # 6 down minus 350
        A(17) == A(25) * A(23),       # 25 across times 23 across
        17 * A(25) == A(20),          # 20 across divided by seventeen
        4 * A(27) == D(6),            # 6 down divided by four
        A(28) == 48,                  # four dozen
        A(29) == 1008,                # seven gross
        A(30) == D(22) + 450,         # 22 down plus 450
        D(1) == A(1) + 27,            # 1 across plus twenty-seven
        D(2) == 60,                   # five dozen
        D(3) == A(30) + 888,          # 30 across plus 888
        D(4) == 2 * A(17),            # two times 17 across
        12 * D(5) == A(29),           # 29 across divided by twelve
        D(6) == A(28) * A(23),        # 28 across times 23 across
        D(10) == A(10) + 4,           # 10 across plus four
        D(12) == 3 * A(24),           # three times 24 across
        16 * D(14) == A(13),          # 13 across divided by sixteen
        D(16) == D(28) * 15,          # 28 down times fifteen
        D(17) == A(13) - 399,         # 13 across minus 399
        18 * D(18) == A(29),          # 29 across divided by eighteen
        D(19) == D(22) - 94,          # 22 down minus ninety-four
        D(20) == A(20) - 9,           # 20 across minus nine
        D(21) == A(25) - 52,          # 25 across minus fifty-two
        D(22) == D(20) * 6,           # 20 down times six
        D(26) == 5 * A(24),           # five times 24 across
        D(28) == D(21) + 27,          # 21 down plus twenty-seven
    ]
    for clue in clues:
        model.constraint(clue)
    # 20 across and 24 across are square numbers
    for n in (20, 24):
        root = model.int(1, 99)  # the square root of the entry
        model.constraint(A(n) == root * root)
    # 23 across is a prime number: a two-digit number with no divisor from 2 to 9 other than itself
    for d in range(2, 10):
        model.constraint(model.or_(A(23) == d, A(23) % d != 0))

    return optimizer, {"M": digit}

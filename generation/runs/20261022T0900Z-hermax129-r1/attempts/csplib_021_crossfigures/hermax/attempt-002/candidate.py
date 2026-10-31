from hermax.model import Model

# The puzzle grid of this problem (fixed constants): X is a black square, _ is a blank
# square to fill, and a number labels the start of an Across and/or Down answer.
GRID = [
    "1 2 _ 3 X 4 _ 5 6",
    "7 _ X 8 _ _ X 9 _",
    "_ X 10 _ X 11 12 X _",
    "13 14 _ _ X 15 _ 16 _",
    "X _ X X X X X _ X",
    "17 _ 18 19 X 20 21 _ 22",
    "_ X 23 _ X 24 _ X _",
    "25 26 X 27 _ _ X 28 _",
    "29 _ _ _ X 30 _ _ _",
]


def _answers():
    """Return (R, C, white, words); words maps ('A', n) or ('D', n) to its squares, row-major."""
    rows = [line.split() for line in GRID]
    R = len(rows)
    C = len(rows[0])
    white = [[tok != "X" for tok in row] for row in rows]
    words = {}
    for r in range(R):
        for c in range(C):
            if not white[r][c]:
                continue
            tok = rows[r][c]
            label = int(tok) if tok.isdigit() else None
            # an Across answer starts where the square to the left is black or outside the grid
            if (c == 0 or not white[r][c - 1]) and c + 1 < C and white[r][c + 1]:
                run = []
                cc = c
                while cc < C and white[r][cc]:
                    run.append((r, cc))
                    cc += 1
                words[("A", label)] = run
            # a Down answer starts where the square above is black or outside the grid
            if (r == 0 or not white[r - 1][c]) and r + 1 < R and white[r + 1][c]:
                run = []
                rr = r
                while rr < R and white[rr][c]:
                    run.append((rr, c))
                    rr += 1
                words[("D", label)] = run
    return R, C, white, words


def build(instance):
    R, C, white, words = _answers()

    m = Model()
    # Digit of each square; 0 for black squares (the output).
    M = m.int_matrix("M", R, C, 0, 9)
    for r in range(R):
        for c in range(C):
            if not white[r][c]:
                m &= (M[r][c] == 0)

    # An answer of L squares is an L-digit number with no leading zero.
    # Two-digit answers get an IntVar (small domain). Longer answers are written as the
    # weighted sum of their digits, which avoids wide integer domains.
    def digits_value(cells):
        L = len(cells)
        return sum(10 ** (L - 1 - k) * M[r][c] for k, (r, c) in enumerate(cells))

    val = {}
    for key, cells in words.items():
        if len(cells) == 2:
            name = f"v{key[0]}{key[1]}"
            v = m.int(name, 10, 99)
            m &= (v == digits_value(cells))
            val[key] = v
        else:
            val[key] = digits_value(cells)

    def W(kind, n):
        return val[(kind, n)]

    # Clues with a fixed value from the clue text.
    # 10 Across: a dozen in six gross (6 * 144 / 12 = 72).
    m &= (W("A", 10) == 72)
    # 28 Across: four dozen (48).
    m &= (W("A", 28) == 48)
    # 29 Across: seven gross (7 * 144 = 1008).
    m &= (W("A", 29) == 1008)
    # 2 Down: five dozen (60).
    m &= (W("D", 2) == 60)

    # 20 Across is a square number: 20 Across = r20 * r20 for some root r20.
    # 20 Across is divided by seventeen (25 Across), and 17 is prime, so the root is a multiple of 17.
    r20 = m.int("root_A20", 32, 99)
    for k in range(32, 100):
        if k % 17:
            m &= (r20 != k)
        else:
            m &= (W("A", 20) == k * k).only_if(r20 == k)
    # 24 Across is a square number (two digits, so the root is 4 to 9).
    r24 = m.int("root_A24", 4, 9)
    for k in range(4, 10):
        m &= (W("A", 24) == k * k).only_if(r24 == k)
    # 23 Across is a prime number: forbid every two-digit composite.
    primes = {11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97}
    for v in range(10, 100):
        if v not in primes:
            m &= (W("A", 23) != v)

    # 25 Across: 20 Across divided by seventeen.
    m &= (W("A", 20) == 17 * W("A", 25))
    # 17 Across: 25 Across times 23 Across, so 17 * (17 Across) = 20 Across * 23 Across.
    for k in range(34, 100, 17):
        m &= (17 * W("A", 17) == (k * k) * W("A", 23)).only_if(r20 == k)
    # 13 Across: 26 Down times 23 Across, and 26 Down is five times 24 Across.
    for k in range(4, 10):
        m &= (W("A", 13) == 5 * (k * k) * W("A", 23)).only_if(r24 == k)

    # 1 Across: 27 Across times two.
    m &= (W("A", 1) == 2 * W("A", 27))
    # 4 Across: 4 Down plus seventy-one.
    m &= (W("A", 4) == W("D", 4) + 71)
    # 7 Across: 18 Down plus four.
    m &= (W("A", 7) == W("D", 18) + 4)
    # 8 Across: 6 Down divided by sixteen.
    m &= (W("D", 6) == 16 * W("A", 8))
    # 9 Across: 2 Down minus eighteen.
    m &= (W("A", 9) == W("D", 2) - 18)
    # 11 Across: 5 Down minus seventy.
    m &= (W("A", 11) == W("D", 5) - 70)
    # 15 Across: 6 Down minus 350.
    m &= (W("A", 15) == W("D", 6) - 350)
    # 27 Across: 6 Down divided by four.
    m &= (W("D", 6) == 4 * W("A", 27))
    # 30 Across: 22 Down plus 450.
    m &= (W("A", 30) == W("D", 22) + 450)

    # 6 Down: 28 Across times 23 Across (28 Across is the fixed 48).
    m &= (W("D", 6) == 48 * W("A", 23))
    # 1 Down: 1 Across plus twenty-seven.
    m &= (W("D", 1) == W("A", 1) + 27)
    # 3 Down: 30 Across plus 888.
    m &= (W("D", 3) == W("A", 30) + 888)
    # 4 Down: two times 17 Across.
    m &= (W("D", 4) == 2 * W("A", 17))
    # 5 Down: 29 Across divided by twelve.
    m &= (W("A", 29) == 12 * W("D", 5))
    # 10 Down: 10 Across plus four.
    m &= (W("D", 10) == W("A", 10) + 4)
    # 12 Down: three times 24 Across.
    m &= (W("D", 12) == 3 * W("A", 24))
    # 14 Down: 13 Across divided by sixteen.
    m &= (W("A", 13) == 16 * W("D", 14))
    # 16 Down: 28 Down times fifteen.
    m &= (W("D", 16) == 15 * W("D", 28))
    # 17 Down: 13 Across minus 399.
    m &= (W("D", 17) == W("A", 13) - 399)
    # 18 Down: 29 Across divided by eighteen.
    m &= (W("A", 29) == 18 * W("D", 18))
    # 19 Down: 22 Down minus ninety-four.
    m &= (W("D", 19) == W("D", 22) - 94)
    # 20 Down: 20 Across minus nine.
    m &= (W("D", 20) == W("A", 20) - 9)
    # 21 Down: 25 Across minus fifty-two.
    m &= (W("D", 21) == W("A", 25) - 52)
    # 22 Down: 20 Down times six.
    m &= (W("D", 22) == 6 * W("D", 20))
    # 26 Down: five times 24 Across.
    m &= (W("D", 26) == 5 * W("A", 24))
    # 28 Down: 21 Down plus twenty-seven.
    m &= (W("D", 28) == W("D", 21) + 27)

    return m, {"M": M}

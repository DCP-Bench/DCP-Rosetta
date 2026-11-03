# csplib_021_crossfigures: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install hermax`) with:
#   python csplib_021_crossfigures.py

import math

from hermax.model import Model

# The grid is fixed by the problem statement: "#" is a black square (it holds 0), "." a white cell.
GRID = ["....#....",
        "..#...#..",
        ".#..#..#.",
        "....#....",
        "#.#####.#",
        "....#....",
        ".#..#..#.",
        "..#...#..",
        "....#...."]

# The entries of the grid, numbered as in the statement: name -> (length, row, column).
# Rows and columns count from 1, as in the statement.
ACROSS = {"A1": (4, 1, 1), "A4": (4, 1, 6), "A7": (2, 2, 1), "A8": (3, 2, 4), "A9": (2, 2, 8),
          "A10": (2, 3, 3), "A11": (2, 3, 6), "A13": (4, 4, 1), "A15": (4, 4, 6),
          "A17": (4, 6, 1), "A20": (4, 6, 6), "A23": (2, 7, 3), "A24": (2, 7, 6),
          "A25": (2, 8, 1), "A27": (3, 8, 4), "A28": (2, 8, 8), "A29": (4, 9, 1),
          "A30": (4, 9, 6)}
DOWN = {"D1": (4, 1, 1), "D2": (2, 1, 2), "D3": (4, 1, 4), "D4": (4, 1, 6), "D5": (2, 1, 8),
        "D6": (4, 1, 9), "D10": (2, 3, 3), "D12": (2, 3, 7), "D14": (3, 4, 2),
        "D16": (3, 4, 8), "D17": (4, 6, 1), "D18": (2, 6, 3), "D19": (4, 6, 4),
        "D20": (4, 6, 6), "D21": (2, 6, 7), "D22": (4, 6, 9), "D26": (2, 8, 2),
        "D28": (2, 8, 8)}


def is_prime(v):
    # true when v is a prime number
    return v >= 2 and all(v % d for d in range(2, math.isqrt(v) + 1))


def digit_rows(numbers, length):
    """The allowed digit tuples for a table over an entry of the given length: each
    number written with exactly `length` digits, leading zeros included."""
    return [tuple(int(ch) for ch in f"{v:0{length}d}") for v in numbers if v < 10 ** length]


def create_model(instance):
    """Crossfigure (CSPLib 21): fill the 9x9 grid with digits so that every across and
    down entry is the number its clue describes. Each clue is a number written in words or
    as a relation to other entries. The grid and the clues are fixed by the statement, so
    the instance carries no data. The output is the solved grid, 0 on black squares."""
    # The problem has no instance fields: the grid, the entries and the clues are fixed.
    m = Model()

    # M[i][j] is the digit in row i+1, column j+1 (0..9), 0 on black squares
    M = m.int_matrix("M", 9, 9, 0, 9)
    for i in range(9):
        for j in range(9):
            if GRID[i][j] == "#":
                m &= (M[i][j] == 0)

    # Each entry is a number, read from its digits: an across entry left to right, a down entry top to bottom.
    # value[name] is the number the entry spells (e.g. 1234 for the digits 1, 2, 3, 4), cells[name] its digits in order.
    value, cells = {}, {}
    for names, across in ((ACROSS, True), (DOWN, False)):
        for name, (length, row, col) in names.items():
            digits = [(row - 1, col - 1 + p) if across else (row - 1 + p, col - 1)
                      for p in range(length)]
            cells[name] = [M[i][j] for i, j in digits]
            value[name] = m.int(name, 0, 10 ** length - 1)
            m &= (value[name] == sum(10 ** (length - 1 - p) * cells[name][p]
                                     for p in range(length)))

    # Shorthand for the number an entry spells.
    def v(name):
        return value[name]

    # Products of two entries: result = multiplicand * multiplier, where the multiplier is
    # one of the given values, so each case is a linear constraint, posted only in that case.
    def times(result, multiplicand, multiplier, multiplier_values):
        nonlocal m  # `m &=` rebinds the name, so the closure must declare it
        for k in multiplier_values:
            m &= (v(result) == k * v(multiplicand)).only_if(v(multiplier) == k)

    squares = [k * k for k in range(1, 100)]          # square numbers below 10000
    primes = [p for p in range(2, 100) if is_prime(p)]  # prime numbers below 100

    # A square number, four digits; a prime number, two digits.
    m &= m.table([value["A20"]], allowed=[(s,) for s in squares])   # 20 across: a square number (all below 10**4)
    m &= m.table(cells["A24"], allowed=digit_rows(squares, 2))   # 24 across: a square number
    m &= m.table(cells["A23"], allowed=digit_rows(primes, 2))    # 23 across: a prime number

    # Across
    m &= (v("A1") == 2 * v("A27"))                    # 1: 27 across times two
    m &= (v("A4") == v("D4") + 71)                    # 4: 4 down plus seventy-one
    m &= (v("A7") == v("D18") + 4)                    # 7: 18 down plus four
    m &= (16 * v("A8") == v("D6"))                    # 8: 6 down divided by sixteen
    m &= (v("A9") + 18 == v("D2"))                    # 9: 2 down minus eighteen
    m &= (12 * v("A10") == 6 * 144)                   # 10: a dozen in six gross, 6 * 144 / 12 = 72
    m &= (v("A11") + 70 == v("D5"))                   # 11: 5 down minus seventy
    times("A13", "D26", "A23", primes)                # 13: 26 down times 23 across
    m &= (v("A15") + 350 == v("D6"))                  # 15: 6 down minus 350
    times("A17", "A25", "A23", primes)                # 17: 25 across times 23 across
    m &= (17 * v("A25") == v("A20"))                  # 25: 20 across divided by seventeen
    m &= (4 * v("A27") == v("D6"))                    # 27: 6 down divided by four
    m &= (v("A28") == 4 * 12)                         # 28: four dozen
    m &= (v("A29") == 7 * 144)                        # 29: seven gross
    m &= (v("A30") == v("D22") + 450)                 # 30: 22 down plus 450

    # Down
    m &= (v("D1") == v("A1") + 27)                    # 1: 1 across plus twenty-seven
    m &= (v("D2") == 5 * 12)                          # 2: five dozen
    m &= (v("D3") == v("A30") + 888)                  # 3: 30 across plus 888
    m &= (v("D4") == 2 * v("A17"))                    # 4: two times 17 across
    m &= (12 * v("D5") == v("A29"))                   # 5: 29 across divided by twelve
    times("D6", "A28", "A23", primes)                 # 6: 28 across times 23 across
    m &= (v("D10") == v("A10") + 4)                   # 10: 10 across plus four
    m &= (v("D12") == 3 * v("A24"))                   # 12: three times 24 across
    m &= (16 * v("D14") == v("A13"))                  # 14: 13 across divided by sixteen
    m &= (v("D16") == 15 * v("D28"))                  # 16: 28 down times fifteen
    m &= (v("D17") + 399 == v("A13"))                 # 17: 13 across minus 399
    m &= (18 * v("D18") == v("A29"))                  # 18: 29 across divided by eighteen
    m &= (v("D19") + 94 == v("D22"))                  # 19: 22 down minus ninety-four
    m &= (v("D20") + 9 == v("A20"))                   # 20: 20 across minus nine
    m &= (v("D21") + 52 == v("A25"))                  # 21: 25 across minus fifty-two
    m &= (v("D22") == 6 * v("D20"))                   # 22: 20 down times six
    m &= (v("D26") == 5 * v("A24"))                   # 26: five times 24 across
    m &= (v("D28") == v("D21") + 27)                  # 28: 21 down plus twenty-seven

    return m, {"M": M}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

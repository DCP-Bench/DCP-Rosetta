# csplib_021_crossfigures: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install cpmpy`) with:
#   python csplib_021_crossfigures.py

import math

import cpmpy as cp


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a
    9x9 grid so that every across and down entry is a number that satisfies its
    clue, such as "27 across times two", "a prime number" or "a square number"."""
    # The problem has no instance data: the grid and the clues are fixed by the
    # statement, so they are written out here.
    # The grid, one string per row; '#' is a black cell
    grid = ["....#....",
            "..#...#..",
            ".#..#..#.",
            "....#....",
            "#.#####.#",
            "....#....",
            ".#..#..#.",
            "..#...#..",
            "....#...."]
    n = len(grid)

    # The entries by clue number, as (number of digits, row, column) of the first
    # digit, with rows and columns counted from 1
    across_entries = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                      10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                      20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                      28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    down_entries = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
                    6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
                    17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
                    22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    # The numbers a "prime" or "square" clue can take. The longest entry has 4 digits,
    # so these are the primes and squares up to 9999.
    max_number = 9999
    primes = [p for p in range(2, max_number + 1)
              if all(p % d for d in range(2, math.isqrt(p) + 1))]
    squares = [i * i for i in range(1, math.isqrt(max_number) + 1)]

    # M[r, c] is the digit in row r, column c of the grid; a black cell holds 0
    M = cp.intvar(0, 9, shape=(n, n), name="M")

    model = cp.Model()

    # Black cells hold no digit.
    for r in range(n):
        for c in range(n):
            if grid[r][c] == "#":
                model.add(M[r, c] == 0)

    # across[k] and down[k] are the numbers spelled by the digits of the across and
    # down entry with clue number k. Leading zeros are allowed.
    across, down = {}, {}
    for entries, numbers, name in ((across_entries, across, "across"), (down_entries, down, "down")):
        for k, (length, row, col) in entries.items():
            if name == "across":
                cells = M[row - 1, col - 1:col - 1 + length]
            else:
                cells = M[row - 1:row - 1 + length, col - 1]
            numbers[k] = cp.intvar(0, 10 ** length - 1, name=f"{name}{k}")
            powers_of_ten = [10 ** (length - 1 - i) for i in range(length)]
            model.add(numbers[k] == cp.sum(cells * powers_of_ten))

    # The across clues.
    model.add(across[1] == 2 * across[27])           # 27 across times two
    model.add(across[4] == down[4] + 71)             # 4 down plus seventy-one
    model.add(across[7] == down[18] + 4)             # 18 down plus four
    model.add(16 * across[8] == down[6])             # 6 down divided by sixteen
    model.add(across[9] == down[2] - 18)             # 2 down minus eighteen
    model.add(12 * across[10] == 6 * 144)            # a dozen in six gross
    model.add(across[11] == down[5] - 70)            # 5 down minus seventy
    model.add(across[13] == down[26] * across[23])   # 26 down times 23 across
    model.add(across[15] == down[6] - 350)           # 6 down minus 350
    model.add(across[17] == across[25] * across[23]) # 25 across times 23 across
    model.add(cp.InDomain(across[20], squares))      # a square number
    model.add(cp.InDomain(across[23], primes))       # a prime number
    model.add(cp.InDomain(across[24], squares))      # a square number
    model.add(17 * across[25] == across[20])         # 20 across divided by seventeen
    model.add(4 * across[27] == down[6])             # 6 down divided by four
    model.add(across[28] == 4 * 12)                  # four dozen
    model.add(across[29] == 7 * 144)                 # seven gross
    model.add(across[30] == down[22] + 450)          # 22 down plus 450

    # The down clues.
    model.add(down[1] == across[1] + 27)             # 1 across plus twenty-seven
    model.add(down[2] == 5 * 12)                     # five dozen
    model.add(down[3] == across[30] + 888)           # 30 across plus 888
    model.add(down[4] == 2 * across[17])            # two times 17 across
    model.add(12 * down[5] == across[29])            # 29 across divided by twelve
    model.add(down[6] == across[28] * across[23])    # 28 across times 23 across
    model.add(down[10] == across[10] + 4)            # 10 across plus four
    model.add(down[12] == across[24] * 3)            # three times 24 across
    model.add(16 * down[14] == across[13])           # 13 across divided by sixteen
    model.add(down[16] == 15 * down[28])             # 28 down times fifteen
    model.add(down[17] == across[13] - 399)          # 13 across minus 399
    model.add(18 * down[18] == across[29])           # 29 across divided by eighteen
    model.add(down[19] == down[22] - 94)             # 22 down minus ninety-four
    model.add(down[20] == across[20] - 9)            # 20 across minus nine
    model.add(down[21] == across[25] - 52)           # 25 across minus fifty-two
    model.add(down[22] == 6 * down[20])              # 20 down times six
    model.add(down[26] == 5 * across[24])            # five times 24 across
    model.add(down[28] == down[21] + 27)             # 21 down plus twenty-seven

    return model, {"M": M}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

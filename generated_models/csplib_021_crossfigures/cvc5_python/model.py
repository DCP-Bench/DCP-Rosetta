# csplib_021_crossfigures: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install cvc5 numpy`) with:
#   python csplib_021_crossfigures.py

import cvc5.pythonic as c5


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a
    9x9 grid so that every across and down entry is a number that satisfies its
    clue, such as "27 across times two", "a prime number" or "a square number"."""
    # The grid: '#' is a black cell, '.' is a white cell.
    grid = ["....#....",
            "..#...#..",
            ".#..#..#.",
            "....#....",
            "#.#####.#",
            "....#....",
            ".#..#..#.",
            "..#...#..",
            "....#...."]
    n_side = len(grid)  # the grid is n_side cells wide and n_side cells high

    # The entries by clue number: the length in digits, and the row and column of the
    # first digit (the top row and the left column are 1).
    across_entries = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                      10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                      20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                      28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    down_entries = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
                    6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
                    17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
                    22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    # The answers to the prime and square clues: two-digit primes, and two-digit and
    # four-digit squares.
    primes2 = [p for p in range(10, 100) if all(p % d for d in range(2, p))]
    squares2 = [k * k for k in range(4, 10)]
    squares4 = [k * k for k in range(32, 100)]

    # A dozen is 12, and a gross is twelve dozen.
    dozen = 12
    gross = 12 * dozen

    # M[r][c] is the digit in row r, column c, counted from 0. A black cell holds 0.
    M = [[c5.Int(f"M_{r}_{c}") if grid[r][c] != "#" else c5.IntVal(0) for c in range(n_side)]
         for r in range(n_side)]

    # The digits of an entry, read as one number with the first digit most significant.
    def number(cells):
        length = len(cells)
        return c5.Sum([cell * 10 ** (length - 1 - i) for i, cell in enumerate(cells)])

    # The cells of each entry, from its first digit onwards.
    across_cells = {k: [M[row - 1][col - 1 + i] for i in range(length)]
                    for k, (length, row, col) in across_entries.items()}
    down_cells = {k: [M[row - 1 + i][col - 1] for i in range(length)]
                  for k, (length, row, col) in down_entries.items()}

    # A is the answer to each across clue, D the answer to each down clue.
    A = {k: number(cells) for k, cells in across_cells.items()}
    D = {k: number(cells) for k, cells in down_cells.items()}

    solver = c5.Solver()

    # Each digit is between 0 and 9.
    solver.add([c5.And(M[r][c] >= 0, M[r][c] <= 9)
                for r in range(n_side) for c in range(n_side) if grid[r][c] != "#"])

    # Each answer has no leading zero.
    solver.add([cells[0] != 0 for cells in list(across_cells.values()) + list(down_cells.values())])

    # Across clues.
    solver.add(A[1] == 2 * A[27])                   # 27 across times two
    solver.add(A[4] == D[4] + 71)                   # 4 down plus seventy-one
    solver.add(A[7] == D[18] + 4)                   # 18 down plus four
    solver.add(D[6] == 16 * A[8])                   # 6 down divided by sixteen
    solver.add(A[9] == D[2] - 18)                   # 2 down minus eighteen
    solver.add(A[10] == 6 * gross // dozen)         # dozen in six gross
    solver.add(A[11] == D[5] - 70)                  # 5 down minus seventy
    solver.add(c5.Or([c5.And(A[23] == p, A[13] == p * D[26]) for p in primes2]))  # 26 down times 23 across
    solver.add(A[15] == D[6] - 350)                 # 6 down minus 350
    solver.add(c5.Or([c5.And(A[23] == p, A[17] == p * A[25]) for p in primes2]))  # 25 across times 23 across
    solver.add(c5.Or([A[20] == s for s in squares4]))  # a square number
    solver.add(c5.Or([A[23] == p for p in primes2]))   # a prime number
    solver.add(c5.Or([A[24] == s for s in squares2]))  # a square number
    solver.add(A[20] == 17 * A[25])                 # 20 across divided by seventeen
    solver.add(D[6] == 4 * A[27])                   # 6 down divided by four
    solver.add(A[28] == 4 * dozen)                  # four dozen
    solver.add(A[29] == 7 * gross)                  # seven gross
    solver.add(A[30] == D[22] + 450)                # 22 down plus 450

    # Down clues.
    solver.add(D[1] == A[1] + 27)                   # 1 across plus twenty-seven
    solver.add(D[2] == 5 * dozen)                   # five dozen
    solver.add(D[3] == A[30] + 888)                 # 30 across plus 888
    solver.add(D[4] == 2 * A[17])                   # two times 17 across
    solver.add(A[29] == dozen * D[5])               # 29 across divided by twelve
    solver.add(D[6] == 4 * dozen * A[23])           # 28 across times 23 across
    solver.add(D[10] == A[10] + 4)                  # 10 across plus four
    solver.add(D[12] == 3 * A[24])                  # three times 24 across
    solver.add(A[13] == 16 * D[14])                 # 13 across divided by sixteen
    solver.add(D[16] == 15 * D[28])                 # 28 down times fifteen
    solver.add(D[17] == A[13] - 399)                # 13 across minus 399
    solver.add(A[29] == 18 * D[18])                 # 29 across divided by eighteen
    solver.add(D[19] == D[22] - 94)                 # 22 down minus ninety-four
    solver.add(D[20] == A[20] - 9)                  # 20 across minus nine
    solver.add(D[21] == A[25] - 52)                 # 25 across minus fifty-two
    solver.add(D[22] == 6 * D[20])                  # 20 down times six
    solver.add(D[26] == 5 * A[24])                  # five times 24 across
    solver.add(D[28] == D[21] + 27)                 # 21 down plus twenty-seven

    # The solved grid, with 0 in the black cells.
    return solver, {"M": M}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

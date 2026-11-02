# csplib_021_crossfigures: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install z3-solver numpy`) with:
#   python csplib_021_crossfigures.py

import math

import z3


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a 9x9 grid so
    that every across and down entry is a number that satisfies its clue, such as "27 across
    times two", "a prime number" or "a square number"."""
    n_side = 9     # the grid has n_side rows and n_side columns
    max_entry = 9999  # an entry has at most four digits

    # The grid, one string per row. X is a black box, and a dot is a square to fill with a digit.
    grid = [
        "....X....",
        "..X...X..",
        ".X..X..X.",
        "....X....",
        "X.XXXXX.X",
        "....X....",
        ".X..X..X.",
        "..X...X..",
        "....X....",
    ]

    # The across entries by clue number: (number of digits, row, column) of the first digit,
    # counting rows and columns from 1.
    across_entries = {
        1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
        10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
        20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
        28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6),
    }
    # The down entries by clue number, with the same layout as the across entries.
    down_entries = {
        1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
        6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
        17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
        22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8),
    }
    # The number of digits in each across entry.
    across_length = {clue: length for clue, (length, _, _) in across_entries.items()}

    # Whether k is a prime number.
    def is_prime(k):
        return k >= 2 and all(k % d for d in range(2, math.isqrt(k) + 1))

    # The entry is a square number that has at most `length` digits.
    def one_of_squares(entry, length):
        return z3.Or([entry == i * i for i in range(1, math.isqrt(10 ** length - 1) + 1)])

    # The entry is a prime number that has at most `length` digits.
    def one_of_primes(entry, length):
        return z3.Or([entry == k for k in range(2, 10 ** length) if is_prime(k)])

    # M[r][c] is the digit in row r, column c. Every square holds a digit from 0 to 9,
    # and a black box holds 0.
    M = [[z3.Int(f"M_{r}_{c}") for c in range(n_side)] for r in range(n_side)]
    solver = z3.Solver()
    for r in range(n_side):
        for c in range(n_side):
            solver.add(z3.And(M[r][c] >= 0, M[r][c] <= 9))
            if grid[r][c] == "X":
                solver.add(M[r][c] == 0)

    # across[k] is the number written by the across entry with clue k, read from its digits
    # left to right. Leading zeros are allowed.
    across = {}
    for clue, (length, row, col) in across_entries.items():
        across[clue] = z3.Int(f"across_{clue}")
        digits = [M[row - 1][col - 1 + i] for i in range(length)]
        solver.add(z3.And(across[clue] >= 0, across[clue] <= max_entry))
        solver.add(across[clue] == z3.Sum([10 ** (length - 1 - i) * d for i, d in enumerate(digits)]))

    # down[k] is the number written by the down entry with clue k, read from its digits
    # top to bottom. Leading zeros are allowed.
    down = {}
    for clue, (length, row, col) in down_entries.items():
        down[clue] = z3.Int(f"down_{clue}")
        digits = [M[row - 1 + i][col - 1] for i in range(length)]
        solver.add(z3.And(down[clue] >= 0, down[clue] <= max_entry))
        solver.add(down[clue] == z3.Sum([10 ** (length - 1 - i) * d for i, d in enumerate(digits)]))

    # The across clues.
    solver.add(
        across[1] == 2 * across[27],    # 1 across: 27 across times two
        across[4] == down[4] + 71,      # 4 across: 4 down plus seventy-one
        across[7] == down[18] + 4,      # 7 across: 18 down plus four
        16 * across[8] == down[6],      # 8 across: 6 down divided by sixteen
        across[9] == down[2] - 18,      # 9 across: 2 down minus eighteen
        12 * across[10] == 6 * 144,     # 10 across: how many dozen are in six gross
        across[11] == down[5] - 70,     # 11 across: 5 down minus seventy
        across[13] == down[26] * across[23],  # 13 across: 26 down times 23 across
        across[15] == down[6] - 350,    # 15 across: 6 down minus 350
        across[17] == across[25] * across[23],  # 17 across: 25 across times 23 across
        17 * across[25] == across[20],  # 25 across: 20 across divided by seventeen
        4 * across[27] == down[6],      # 27 across: 6 down divided by four
        across[28] == 4 * 12,           # 28 across: four dozen
        across[29] == 7 * 144,          # 29 across: seven gross
        across[30] == down[22] + 450,   # 30 across: 22 down plus 450
    )
    solver.add(one_of_squares(across[20], across_length[20]))  # 20 across: a square number
    solver.add(one_of_primes(across[23], across_length[23]))   # 23 across: a prime number
    solver.add(one_of_squares(across[24], across_length[24]))  # 24 across: a square number

    # The down clues.
    solver.add(
        down[1] == across[1] + 27,      # 1 down: 1 across plus twenty-seven
        down[2] == 5 * 12,              # 2 down: five dozen
        down[3] == across[30] + 888,    # 3 down: 30 across plus 888
        down[4] == 2 * across[17],      # 4 down: two times 17 across
        12 * down[5] == across[29],     # 5 down: 29 across divided by twelve
        down[6] == across[28] * across[23],  # 6 down: 28 across times 23 across
        down[10] == across[10] + 4,     # 10 down: 10 across plus four
        down[12] == across[24] * 3,     # 12 down: three times 24 across
        16 * down[14] == across[13],    # 14 down: 13 across divided by sixteen
        down[16] == 15 * down[28],      # 16 down: 28 down times fifteen
        down[17] == across[13] - 399,   # 17 down: 13 across minus 399
        18 * down[18] == across[29],    # 18 down: 29 across divided by eighteen
        down[19] == down[22] - 94,      # 19 down: 22 down minus ninety-four
        down[20] == across[20] - 9,     # 20 down: 20 across minus nine
        down[21] == across[25] - 52,    # 21 down: 25 across minus fifty-two
        down[22] == 6 * down[20],       # 22 down: 20 down times six
        down[26] == 5 * across[24],     # 26 down: five times 24 across
        down[28] == down[21] + 27,      # 28 down: 21 down plus twenty-seven
    )

    return solver, {"M": M}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

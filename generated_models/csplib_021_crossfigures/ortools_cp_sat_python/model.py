# csplib_021_crossfigures: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install ortools`) with:
#   python csplib_021_crossfigures.py

import math

from ortools.sat.python import cp_model


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a
    9x9 grid so that every across and down entry is a number that satisfies its
    clue, such as "27 across times two", "a prime number" or "a square number"."""
    # The grid; '#' is a black cell
    grid = ["....#....",
            "..#...#..",
            ".#..#..#.",
            "....#....",
            "#.#####.#",
            "....#....",
            ".#..#..#.",
            "..#...#..",
            "....#...."]
    n_side = len(grid)  # the grid has n_side rows and n_side columns

    # Each entry by clue number: its number of digits, and the row and column of its
    # first digit, counted from 1
    across_entries = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                      10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                      20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                      28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    down_entries = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
                    6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
                    17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
                    22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    # The numbers a "prime" or "square" clue can take: the primes and squares up to the
    # largest entry.
    all_entries = list(across_entries.values()) + list(down_entries.values())
    max_digits = max(length for length, _, _ in all_entries)
    max_number = 10 ** max_digits - 1
    primes = cp_model.Domain.from_values(
        [p for p in range(2, max_number + 1) if all(p % d for d in range(2, math.isqrt(p) + 1))])
    squares = cp_model.Domain.from_values([i * i for i in range(1, math.isqrt(max_number) + 1)])

    model = cp_model.CpModel()

    # M[r][c] is the digit in row r, column c of the grid
    M = [[model.new_int_var(0, 9, f"M_{r}_{c}") for c in range(n_side)] for r in range(n_side)]

    # Black cells hold no digit.
    for r in range(n_side):
        for c in range(n_side):
            if grid[r][c] == "#":
                model.add(M[r][c] == 0)

    # across[k] and down[k] are the numbers spelled by the digits of the across and
    # down entry with clue number k. Leading zeros are allowed.
    across, down = {}, {}
    for entries, numbers, name in ((across_entries, across, "across"), (down_entries, down, "down")):
        for k, (length, row, col) in entries.items():
            if name == "across":
                # the squares of this entry, from left to right
                cells = [M[row - 1][col - 1 + i] for i in range(length)]
            else:
                # the squares of this entry, from top to bottom
                cells = [M[row - 1 + i][col - 1] for i in range(length)]
            numbers[k] = model.new_int_var(0, 10 ** length - 1, f"{name}{k}")
            model.add(numbers[k] == sum(10 ** (length - 1 - i) * cell for i, cell in enumerate(cells)))

    # The across clues.
    model.add(across[1] == 2 * across[27])                  # 27 across times two
    model.add(across[4] == down[4] + 71)                    # 4 down plus seventy-one
    model.add(across[7] == down[18] + 4)                    # 18 down plus four
    model.add(16 * across[8] == down[6])                    # 6 down divided by sixteen
    model.add(across[9] == down[2] - 18)                    # 2 down minus eighteen
    model.add(12 * across[10] == 6 * 144)                   # a dozen in six gross
    model.add(across[11] == down[5] - 70)                   # 5 down minus seventy
    model.add_multiplication_equality(across[13], [down[26], across[23]])   # 26 down times 23 across
    model.add(across[15] == down[6] - 350)                  # 6 down minus 350
    model.add_multiplication_equality(across[17], [across[25], across[23]]) # 25 across times 23 across
    model.add_linear_expression_in_domain(across[20], squares)  # a square number
    model.add_linear_expression_in_domain(across[23], primes)   # a prime number
    model.add_linear_expression_in_domain(across[24], squares)  # a square number
    model.add(17 * across[25] == across[20])                # 20 across divided by seventeen
    model.add(4 * across[27] == down[6])                    # 6 down divided by four
    model.add(across[28] == 4 * 12)                         # four dozen
    model.add(across[29] == 7 * 144)                        # seven gross
    model.add(across[30] == down[22] + 450)                 # 22 down plus 450

    # The down clues.
    model.add(down[1] == across[1] + 27)                    # 1 across plus twenty-seven
    model.add(down[2] == 5 * 12)                            # five dozen
    model.add(down[3] == across[30] + 888)                  # 30 across plus 888
    model.add(down[4] == 2 * across[17])                    # two times 17 across
    model.add(12 * down[5] == across[29])                   # 29 across divided by twelve
    model.add_multiplication_equality(down[6], [across[28], across[23]])    # 28 across times 23 across
    model.add(down[10] == across[10] + 4)                   # 10 across plus four
    model.add(down[12] == 3 * across[24])                   # three times 24 across
    model.add(16 * down[14] == across[13])                  # 13 across divided by sixteen
    model.add(down[16] == 15 * down[28])                    # 28 down times fifteen
    model.add(down[17] == across[13] - 399)                 # 13 across minus 399
    model.add(18 * down[18] == across[29])                  # 29 across divided by eighteen
    model.add(down[19] == down[22] - 94)                    # 22 down minus ninety-four
    model.add(down[20] == across[20] - 9)                   # 20 across minus nine
    model.add(down[21] == across[25] - 52)                  # 25 across minus fifty-two
    model.add(down[22] == 6 * down[20])                     # 20 down times six
    model.add(down[26] == 5 * across[24])                   # five times 24 across
    model.add(down[28] == down[21] + 27)                    # 21 down plus twenty-seven

    return model, {"M": M}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

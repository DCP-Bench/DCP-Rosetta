# csplib_021_crossfigures: a PuLP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install pulp numpy`) with:
#   python csplib_021_crossfigures.py

import math

import pulp


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a
    9x9 grid so that every across and down entry is a number that satisfies its
    clue, such as "27 across times two", "a prime number" or "a square number"."""
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

    problem = pulp.LpProblem("crossfigures", pulp.LpMinimize)

    # M[r][c] is the digit in row r, column c of the grid. A black cell holds no digit, so it is 0.
    M = [[0 if grid[r][c] == "#" else pulp.LpVariable(f"M_{r}_{c}", 0, 9, cat="Integer")
          for c in range(n_side)]
         for r in range(n_side)]

    # The number an entry spells, read from its first digit onward.
    def across_number(length, row, col):
        return pulp.lpSum(10 ** (length - 1 - i) * M[row - 1][col - 1 + i] for i in range(length))

    def down_number(length, row, col):
        return pulp.lpSum(10 ** (length - 1 - i) * M[row - 1 + i][col - 1] for i in range(length))

    # across[k] and down[k] are the numbers in the entries with clue number k.
    across = {k: across_number(*entry) for k, entry in across_entries.items()}
    down = {k: down_number(*entry) for k, entry in down_entries.items()}

    # The primes below 100, the values 23 across can take.
    primes = [p for p in range(2, 100) if all(p % q for q in range(2, math.isqrt(p) + 1))]

    # prime[p] is 1 when 23 across is the prime p.
    prime = {p: pulp.LpVariable(f"prime_{p}", cat="Binary") for p in primes}

    # The product of the number other, which lies in 0..largest, and 23 across. For each
    # prime p, share[p] is other when 23 across is p and 0 otherwise, and the product is
    # the sum of p * share[p].
    def times_across_23(other, name, largest):
        share = {p: pulp.LpVariable(f"{name}_{p}", 0, largest) for p in primes}
        for p, chosen in prime.items():
            problem.addConstraint(share[p] <= largest * chosen)
            problem.addConstraint(share[p] <= other)
            problem.addConstraint(share[p] >= other - largest * (1 - chosen))
        return pulp.lpSum(p * share[p] for p in primes)

    # The entry is a square number: one root r is chosen, and the entry is r * r. The
    # roots are those whose squares have at most as many digits as the entry.
    def square_number(expression, digits, name):
        roots = range(1, math.isqrt(10 ** digits - 1) + 1)
        root = {r: pulp.LpVariable(f"{name}_{r}", cat="Binary") for r in roots}
        problem.addConstraint(pulp.lpSum(root.values()) == 1)
        problem.addConstraint(expression == pulp.lpSum(r * r * chosen for r, chosen in root.items()))

    # 23 across is one of the primes.
    problem += pulp.lpSum(prime.values()) == 1
    problem += across[23] == pulp.lpSum(p * chosen for p, chosen in prime.items())

    # Across clues.
    problem += across[1] == 2 * across[27]                      # 27 across times two
    problem += across[4] == down[4] + 71                        # 4 down plus seventy-one
    problem += across[7] == down[18] + 4                        # 18 down plus four
    problem += 16 * across[8] == down[6]                        # 6 down divided by sixteen
    problem += across[9] == down[2] - 18                        # 2 down minus eighteen
    problem += 12 * across[10] == 6 * 144                       # a dozen in six gross
    problem += across[11] == down[5] - 70                       # 5 down minus seventy
    problem += across[13] == times_across_23(down[26], "d26_times_23", 99)  # 26 down times 23 across
    problem += across[15] == down[6] - 350                      # 6 down minus 350
    problem += across[17] == times_across_23(across[25], "a25_times_23", 99)  # 25 across times 23 across
    square_number(across[20], 4, "root_20")                     # a square number
    square_number(across[24], 2, "root_24")                     # a square number
    problem += 17 * across[25] == across[20]                    # 20 across divided by seventeen
    problem += 4 * across[27] == down[6]                        # 6 down divided by four
    problem += across[28] == 4 * 12                             # four dozen
    problem += across[29] == 7 * 144                            # seven gross
    problem += across[30] == down[22] + 450                     # 22 down plus 450

    # Down clues.
    problem += down[1] == across[1] + 27                        # 1 across plus twenty-seven
    problem += down[2] == 5 * 12                                # five dozen
    problem += down[3] == across[30] + 888                      # 30 across plus 888
    problem += down[4] == 2 * across[17]                        # two times 17 across
    problem += 12 * down[5] == across[29]                       # 29 across divided by twelve
    problem += down[6] == 4 * 12 * across[23]                   # 28 across times 23 across, 28 across being four dozen
    problem += down[10] == across[10] + 4                       # 10 across plus four
    problem += down[12] == 3 * across[24]                       # three times 24 across
    problem += 16 * down[14] == across[13]                      # 13 across divided by sixteen
    problem += down[16] == 15 * down[28]                        # 28 down times fifteen
    problem += down[17] == across[13] - 399                     # 13 across minus 399
    problem += 18 * down[18] == across[29]                      # 29 across divided by eighteen
    problem += down[19] == down[22] - 94                        # 22 down minus ninety-four
    problem += down[20] == across[20] - 9                       # 20 across minus nine
    problem += down[21] == across[25] - 52                      # 25 across minus fifty-two
    problem += down[22] == 6 * down[20]                         # 20 down times six
    problem += down[26] == 5 * across[24]                       # five times 24 across
    problem += down[28] == down[21] + 27                        # 21 down plus twenty-seven

    return problem, {"M": M}


if __name__ == "__main__":
    import numpy as np

    problem, outputs = create_model({})
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

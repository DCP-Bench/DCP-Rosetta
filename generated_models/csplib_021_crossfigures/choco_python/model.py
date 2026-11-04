# csplib_021_crossfigures: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install pychoco numpy`) with:
#   python csplib_021_crossfigures.py

import math

from pychoco.model import Model


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a
    9x9 grid so that every across and down entry is a number that satisfies its
    clue, such as "27 across times two", "a prime number" or "a square number"."""
    # The grid: '#' is a black square, '.' an empty one.
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

    # Across entries by clue number: (number of digits, row, column of the first digit),
    # with rows and columns counted from 1.
    across_entries = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
                      10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
                      20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
                      28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    # Down entries, in the same form.
    down_entries = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
                    6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
                    17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
                    22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    # The longest entry sets the largest number any entry can hold.
    all_entries = list(across_entries.values()) + list(down_entries.values())
    max_number = 10 ** max(length for length, _, _ in all_entries) - 1
    # The primes and squares up to that number, for the prime and square clues.
    primes = [p for p in range(2, max_number + 1)
              if all(p % d for d in range(2, math.isqrt(p) + 1))]
    squares = [r * r for r in range(1, math.isqrt(max_number) + 1)]

    model = Model()

    # M[r][c] is the digit in row r, column c; a black square holds 0.
    M = [[model.intvar(0, 0 if grid[r][c] == "#" else 9, name=f"M_{r}_{c}") for c in range(n_side)]
         for r in range(n_side)]

    # A[k] is the number of across entry k, and Dn[k] the number of down entry k.
    A = {k: model.intvar(0, 10 ** length - 1, name=f"A{k}", bounded_domain=True)
         for k, (length, _, _) in across_entries.items()}
    Dn = {k: model.intvar(0, 10 ** length - 1, name=f"D{k}", bounded_domain=True)
          for k, (length, _, _) in down_entries.items()}

    # The number of each entry is the number its digits spell, read left to right
    # for across entries and top to bottom for down entries.
    for entries, numbers, dr, dc in ((across_entries, A, 0, 1), (down_entries, Dn, 1, 0)):
        for k, (length, row, col) in entries.items():
            cells = [M[row - 1 + dr * t][col - 1 + dc * t] for t in range(length)]
            model.scalar(cells, [10 ** (length - t - 1) for t in range(length)], "=", numbers[k]).post()

    # The across clues.
    model.scalar([A[1], A[27]], [1, -2], "=", 0).post()          # 1 across: 27 across times two
    model.scalar([A[4], Dn[4]], [1, -1], "=", 71).post()         # 4 across: 4 down plus seventy-one
    model.scalar([A[7], Dn[18]], [1, -1], "=", 4).post()         # 7 across: 18 down plus four
    model.scalar([Dn[6], A[8]], [1, -16], "=", 0).post()         # 8 across: 6 down divided by sixteen
    model.scalar([A[9], Dn[2]], [1, -1], "=", -18).post()        # 9 across: 2 down minus eighteen
    model.arithm(A[10], "=", 6 * 144 // 12).post()               # 10 across: dozens in six gross
    model.scalar([A[11], Dn[5]], [1, -1], "=", -70).post()       # 11 across: 5 down minus seventy
    model.times(Dn[26], A[23], A[13]).post()                     # 13 across: 26 down times 23 across
    model.scalar([A[15], Dn[6]], [1, -1], "=", -350).post()      # 15 across: 6 down minus 350
    model.times(A[25], A[23], A[17]).post()                      # 17 across: 25 across times 23 across
    model.member(A[20], squares).post()                          # 20 across: a square number
    model.member(A[23], primes).post()                           # 23 across: a prime number
    model.member(A[24], squares).post()                          # 24 across: a square number
    model.scalar([A[20], A[25]], [1, -17], "=", 0).post()        # 25 across: 20 across divided by seventeen
    model.scalar([Dn[6], A[27]], [1, -4], "=", 0).post()         # 27 across: 6 down divided by four
    model.arithm(A[28], "=", 4 * 12).post()                      # 28 across: four dozen
    model.arithm(A[29], "=", 7 * 144).post()                     # 29 across: seven gross
    model.scalar([A[30], Dn[22]], [1, -1], "=", 450).post()      # 30 across: 22 down plus 450

    # The down clues.
    model.scalar([Dn[1], A[1]], [1, -1], "=", 27).post()         # 1 down: 1 across plus twenty-seven
    model.arithm(Dn[2], "=", 5 * 12).post()                      # 2 down: five dozen
    model.scalar([Dn[3], A[30]], [1, -1], "=", 888).post()       # 3 down: 30 across plus 888
    model.scalar([Dn[4], A[17]], [1, -2], "=", 0).post()         # 4 down: two times 17 across
    model.scalar([A[29], Dn[5]], [1, -12], "=", 0).post()        # 5 down: 29 across divided by twelve
    model.times(A[28], A[23], Dn[6]).post()                      # 6 down: 28 across times 23 across
    model.scalar([Dn[10], A[10]], [1, -1], "=", 4).post()        # 10 down: 10 across plus four
    model.scalar([Dn[12], A[24]], [1, -3], "=", 0).post()        # 12 down: three times 24 across
    model.scalar([A[13], Dn[14]], [1, -16], "=", 0).post()       # 14 down: 13 across divided by sixteen
    model.scalar([Dn[16], Dn[28]], [1, -15], "=", 0).post()      # 16 down: 28 down times fifteen
    model.scalar([Dn[17], A[13]], [1, -1], "=", -399).post()     # 17 down: 13 across minus 399
    model.scalar([A[29], Dn[18]], [1, -18], "=", 0).post()       # 18 down: 29 across divided by eighteen
    model.scalar([Dn[19], Dn[22]], [1, -1], "=", -94).post()     # 19 down: 22 down minus ninety-four
    model.scalar([Dn[20], A[20]], [1, -1], "=", -9).post()       # 20 down: 20 across minus nine
    model.scalar([Dn[21], A[25]], [1, -1], "=", -52).post()      # 21 down: 25 across minus fifty-two
    model.scalar([Dn[22], Dn[20]], [1, -6], "=", 0).post()       # 22 down: 20 down times six
    model.scalar([Dn[26], A[24]], [1, -5], "=", 0).post()        # 26 down: five times 24 across
    model.scalar([Dn[28], Dn[21]], [1, -1], "=", 27).post()      # 28 down: 21 down plus twenty-seven

    return model, {"M": M}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

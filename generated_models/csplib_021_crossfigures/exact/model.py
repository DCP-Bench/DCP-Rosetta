# csplib_021_crossfigures: an Exact (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install exact numpy`) with:
#   python csplib_021_crossfigures.py

from math import isqrt

from exact import Exact


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: place digits in a
    9x9 grid so that every across and down entry is a number that satisfies its
    clue, such as "27 across times two", "a prime number" or "a square number"."""
    # The grid, one string per row. '#' is a black cell, '.' a white cell.
    layout = ["....#....",
              "..#...#..",
              ".#..#..#.",
              "....#....",
              "#.#####.#",
              "....#....",
              ".#..#..#.",
              "..#...#..",
              "....#...."]
    n_side = len(layout)  # the grid is n_side cells wide and high

    # The across entries, by clue name: (number of digits, row, column) of the first
    # digit, with rows and columns counted from 1.
    across = {"A1": (4, 1, 1), "A4": (4, 1, 6), "A7": (2, 2, 1), "A8": (3, 2, 4), "A9": (2, 2, 8),
              "A10": (2, 3, 3), "A11": (2, 3, 6), "A13": (4, 4, 1), "A15": (4, 4, 6),
              "A17": (4, 6, 1), "A20": (4, 6, 6), "A23": (2, 7, 3), "A24": (2, 7, 6),
              "A25": (2, 8, 1), "A27": (3, 8, 4), "A28": (2, 8, 8), "A29": (4, 9, 1),
              "A30": (4, 9, 6)}
    # The down entries, by clue name, in the same form.
    down = {"D1": (4, 1, 1), "D2": (2, 1, 2), "D3": (4, 1, 4), "D4": (4, 1, 6), "D5": (2, 1, 8),
            "D6": (4, 1, 9), "D10": (2, 3, 3), "D12": (2, 3, 7), "D14": (3, 4, 2),
            "D16": (3, 4, 8), "D17": (4, 6, 1), "D18": (2, 6, 3), "D19": (4, 6, 4),
            "D20": (4, 6, 6), "D21": (2, 6, 7), "D22": (4, 6, 9), "D26": (2, 8, 2),
            "D28": (2, 8, 8)}
    length_of = {name: length for name, (length, _, _) in {**across, **down}.items()}

    # The longest entry has this many digits, so no entry can be larger than top.
    top = 10 ** max(length_of.values()) - 1
    # The prime numbers and square numbers up to top.
    primes = [p for p in range(2, top + 1) if all(p % d for d in range(2, isqrt(p) + 1))]
    squares = [i * i for i in range(1, isqrt(top) + 1)]

    solver = Exact()

    # Exact identifies its variables by name.
    # M[i][j] is the digit in row i, column j, counted from 0. A black cell holds 0, a white
    # cell a digit from 0 to 9.
    M = [[f"M_{i}_{j}" for j in range(n_side)] for i in range(n_side)]
    for i in range(n_side):
        for j in range(n_side):
            solver.addVariable(M[i][j], 0, 0 if layout[i][j] == "#" else 9)

    # An entry is the number spelled by its cells, read from the first digit to the last.
    # Leading zeros are allowed.
    def entry(name, length, cells):
        solver.addVariable(name, 0, 10 ** length - 1)
        solver.addConstraint([(1, name)] + [(-(10 ** (length - 1 - k)), cells[k])
                                            for k in range(length)], True, 0, True, 0)

    # Every entry spells its number from the cells of the grid it runs through.
    for name, (length, row, col) in across.items():
        entry(name, length, [M[row - 1][col - 1 + k] for k in range(length)])
    for name, (length, row, col) in down.items():
        entry(name, length, [M[row - 1 + k][col - 1] for k in range(length)])

    def equals(terms, value=0):
        # The weighted sum of the entries equals value.
        solver.addConstraint(terms, True, value, True, value)

    def times(result, factor_a, factor_b):
        # result is factor_a times factor_b.
        solver.addMultiplication([factor_a, factor_b], True, result, True, result)

    def one_of(name, allowed, label):
        # name_label_v is 1 when the entry name is v. Only values that fit the entry's digits
        # are considered.
        allowed = [v for v in allowed if v <= 10 ** length_of[name] - 1]
        picks = [f"{name}_is_{label}_{v}" for v in allowed]
        for pick in picks:
            solver.addVariable(pick, 0, 1)
        # Exactly one allowed value is taken.
        solver.addConstraint([(1, pick) for pick in picks], True, 1, True, 1)
        # The entry is the value whose pick is set.
        solver.addConstraint([(v, pick) for v, pick in zip(allowed, picks)] + [(-1, name)],
                             True, 0, True, 0)

    # The across clues.
    equals([(1, "A1"), (-2, "A27")])               # 1 across: 27 across times two
    equals([(1, "A4"), (-1, "D4")], 71)            # 4 across: 4 down plus seventy-one
    equals([(1, "A7"), (-1, "D18")], 4)            # 7 across: 18 down plus four
    equals([(16, "A8"), (-1, "D6")])               # 8 across: 6 down divided by sixteen
    equals([(1, "A9"), (-1, "D2")], -18)           # 9 across: 2 down minus eighteen
    equals([(12, "A10")], 6 * 144)                 # 10 across: a dozen in six gross
    equals([(1, "A11"), (-1, "D5")], -70)          # 11 across: 5 down minus seventy
    times("A13", "D26", "A23")                     # 13 across: 26 down times 23 across
    equals([(1, "A15"), (-1, "D6")], -350)         # 15 across: 6 down minus 350
    times("A17", "A25", "A23")                     # 17 across: 25 across times 23 across
    one_of("A20", squares, "square")               # 20 across: a square number
    one_of("A23", primes, "prime")                 # 23 across: a prime number
    one_of("A24", squares, "square")               # 24 across: a square number
    equals([(17, "A25"), (-1, "A20")])             # 25 across: 20 across divided by seventeen
    equals([(4, "A27"), (-1, "D6")])               # 27 across: 6 down divided by four
    equals([(1, "A28")], 4 * 12)                   # 28 across: four dozen
    equals([(1, "A29")], 7 * 144)                  # 29 across: seven gross
    equals([(1, "A30"), (-1, "D22")], 450)         # 30 across: 22 down plus 450

    # The down clues.
    equals([(1, "D1"), (-1, "A1")], 27)            # 1 down: 1 across plus twenty-seven
    equals([(1, "D2")], 5 * 12)                    # 2 down: five dozen
    equals([(1, "D3"), (-1, "A30")], 888)          # 3 down: 30 across plus 888
    equals([(1, "D4"), (-2, "A17")])               # 4 down: two times 17 across
    equals([(12, "D5"), (-1, "A29")])              # 5 down: 29 across divided by twelve
    times("D6", "A28", "A23")                      # 6 down: 28 across times 23 across
    equals([(1, "D10"), (-1, "A10")], 4)           # 10 down: 10 across plus four
    equals([(1, "D12"), (-3, "A24")])              # 12 down: three times 24 across
    equals([(16, "D14"), (-1, "A13")])             # 14 down: 13 across divided by sixteen
    equals([(1, "D16"), (-15, "D28")])             # 16 down: 28 down times fifteen
    equals([(1, "D17"), (-1, "A13")], -399)        # 17 down: 13 across minus 399
    equals([(18, "D18"), (-1, "A29")])             # 18 down: 29 across divided by eighteen
    equals([(1, "D19"), (-1, "D22")], -94)         # 19 down: 22 down minus ninety-four
    equals([(1, "D20"), (-1, "A20")], -9)          # 20 down: 20 across minus nine
    equals([(1, "D21"), (-1, "A25")], -52)         # 21 down: 25 across minus fifty-two
    equals([(1, "D22"), (-6, "D20")])              # 22 down: 20 down times six
    equals([(1, "D26"), (-5, "A24")])              # 26 down: five times 24 across
    equals([(1, "D28"), (-1, "D21")], 27)          # 28 down: 21 down plus twenty-seven

    return solver, {"M": M}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

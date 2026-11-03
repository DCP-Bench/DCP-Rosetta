# csplib_021_crossfigures: a PySAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install "python-sat[pblib]" numpy`) with:
#   python csplib_021_crossfigures.py

from math import isqrt

from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Fill a 9x9 grid with digits so that every across and down entry, a number written in
    the grid, has the value its clue states: a multiple or sum of other entries, a dozen, a
    square or a prime. The problem has no instance data; the grid and clues are fixed."""
    # layout[i] is row i of the grid; '#' is a black square, '.' a square that takes a digit.
    layout = ["....#....",
              "..#...#..",
              ".#..#..#.",
              "....#....",
              "#.#####.#",
              "....#....",
              ".#..#..#.",
              "..#...#..",
              "....#...."]
    n = len(layout)

    # across[number] is (number of digits, row, column) of the first square of the across entry
    # with that clue number. Rows and columns count from 1, as in the puzzle.
    across = {1: (4, 1, 1), 4: (4, 1, 6), 7: (2, 2, 1), 8: (3, 2, 4), 9: (2, 2, 8),
              10: (2, 3, 3), 11: (2, 3, 6), 13: (4, 4, 1), 15: (4, 4, 6), 17: (4, 6, 1),
              20: (4, 6, 6), 23: (2, 7, 3), 24: (2, 7, 6), 25: (2, 8, 1), 27: (3, 8, 4),
              28: (2, 8, 8), 29: (4, 9, 1), 30: (4, 9, 6)}
    # down[number] is (number of digits, row, column) of the first square of the down entry.
    down = {1: (4, 1, 1), 2: (2, 1, 2), 3: (4, 1, 4), 4: (4, 1, 6), 5: (2, 1, 8),
            6: (4, 1, 9), 10: (2, 3, 3), 12: (2, 3, 7), 14: (3, 4, 2), 16: (3, 4, 8),
            17: (4, 6, 1), 18: (2, 6, 3), 19: (4, 6, 4), 20: (4, 6, 6), 21: (2, 6, 7),
            22: (4, 6, 9), 26: (2, 8, 2), 28: (2, 8, 8)}

    pool = IDPool()
    # M[i][j] is the digit in row i, column j, counting from 0. A black square holds 0.
    M = [[Integer(f"M{i}_{j}", 0, 9, vpool=pool) for j in range(n)] for i in range(n)]
    engine = IntegerEngine(vars=[cell for row in M for cell in row], vpool=pool)
    cnf = engine.clausify()

    # Black squares hold 0.
    for i in range(n):
        for j in range(n):
            if layout[i][j] == "#":
                cnf.append([M[i][j].equals(0)])

    # spells[name][v] is true when the digits of the entry name, read as a number with leading
    # zeros allowed, are v. The clue answers are linked to each other through these values.
    spells = {}
    length = {}  # length[name]: the number of digits of the entry name

    def define(name, digits, row, col, step):
        """The entry name starts at (row, col) and runs over the squares in the direction step."""
        cells = [M[row - 1 + step[0] * k][col - 1 + step[1] * k] for k in range(digits)]
        length[name] = digits
        spells[name] = []
        for v in range(10 ** digits):
            is_v = pool.id(("value", name, v))
            spells[name].append(is_v)
            written = str(v).zfill(digits)
            cnf.append([-cell.equals(int(d)) for cell, d in zip(cells, written)] + [is_v])
            for cell, d in zip(cells, written):
                cnf.append([-is_v, cell.equals(int(d))])

    for number, (digits, row, col) in across.items():
        define(f"A{number}", digits, row, col, (0, 1))
    for number, (digits, row, col) in down.items():
        define(f"D{number}", digits, row, col, (1, 0))

    def linear(a, x, b, y, c):
        """a * x == b * y + c for two clue answers x and y."""
        for value in range(10 ** length[y]):
            rhs = b * value + c
            if rhs % a == 0 and 0 <= rhs // a < 10 ** length[x]:
                cnf.append([-spells[y][value], spells[x][rhs // a]])
            else:
                cnf.append([-spells[y][value]])
        for value in range(10 ** length[x]):
            lhs = a * value - c
            if lhs % b == 0 and 0 <= lhs // b < 10 ** length[y]:
                cnf.append([-spells[x][value], spells[y][lhs // b]])
            else:
                cnf.append([-spells[x][value]])

    def fixed(a, x, rhs):
        """a * x == rhs for a clue answer x, where rhs is a number the clue gives."""
        if rhs % a == 0 and 0 <= rhs // a < 10 ** length[x]:
            cnf.append([spells[x][rhs // a]])
        else:
            cnf.append([])

    def product(x, y, z):
        """x == y * z for three clue answers."""
        for u in range(10 ** length[y]):
            for v in range(10 ** length[z]):
                if u * v < 10 ** length[x]:
                    cnf.append([-spells[y][u], -spells[z][v], spells[x][u * v]])
                else:
                    cnf.append([-spells[y][u], -spells[z][v]])

    def member(x, values):
        """x is one of the given values."""
        cnf.append([spells[x][v] for v in values if v < 10 ** length[x]])

    def is_prime(k):
        return k >= 2 and all(k % d for d in range(2, isqrt(k) + 1))

    # The longest entry has four digits, so the primes and squares up to 9999 cover every clue.
    largest = 9999
    primes = [k for k in range(2, largest + 1) if is_prime(k)]
    squares = [k * k for k in range(1, 101)]

    # Across clues
    linear(1, "A1", 2, "A27", 0)             # 1 across: 27 across times two
    linear(1, "A4", 1, "D4", 71)             # 4 across: 4 down plus seventy-one
    linear(1, "A7", 1, "D18", 4)             # 7 across: 18 down plus four
    linear(16, "A8", 1, "D6", 0)             # 8 across: 6 down divided by sixteen
    linear(1, "A9", 1, "D2", -18)            # 9 across: 2 down minus eighteen
    fixed(12, "A10", 6 * 144)                # 10 across: the number of dozen in six gross
    linear(1, "A11", 1, "D5", -70)           # 11 across: 5 down minus seventy
    product("A13", "D26", "A23")             # 13 across: 26 down times 23 across
    linear(1, "A15", 1, "D6", -350)          # 15 across: 6 down minus 350
    product("A17", "A25", "A23")             # 17 across: 25 across times 23 across
    member("A20", squares)                   # 20 across: a square number
    member("A23", primes)                    # 23 across: a prime number
    member("A24", squares)                   # 24 across: a square number
    linear(17, "A25", 1, "A20", 0)           # 25 across: 20 across divided by seventeen
    linear(4, "A27", 1, "D6", 0)             # 27 across: 6 down divided by four
    fixed(1, "A28", 4 * 12)                  # 28 across: four dozen
    fixed(1, "A29", 7 * 144)                 # 29 across: seven gross
    linear(1, "A30", 1, "D22", 450)          # 30 across: 22 down plus 450

    # Down clues
    linear(1, "D1", 1, "A1", 27)             # 1 down: 1 across plus twenty-seven
    fixed(1, "D2", 5 * 12)                   # 2 down: five dozen
    linear(1, "D3", 1, "A30", 888)           # 3 down: 30 across plus 888
    linear(1, "D4", 2, "A17", 0)             # 4 down: two times 17 across
    linear(12, "D5", 1, "A29", 0)            # 5 down: 29 across divided by twelve
    product("D6", "A28", "A23")              # 6 down: 28 across times 23 across
    linear(1, "D10", 1, "A10", 4)            # 10 down: 10 across plus four
    linear(1, "D12", 3, "A24", 0)            # 12 down: three times 24 across
    linear(16, "D14", 1, "A13", 0)           # 14 down: 13 across divided by sixteen
    linear(1, "D16", 15, "D28", 0)           # 16 down: 28 down times fifteen
    linear(1, "D17", 1, "A13", -399)         # 17 down: 13 across minus 399
    linear(18, "D18", 1, "A29", 0)           # 18 down: 29 across divided by eighteen
    linear(1, "D19", 1, "D22", -94)          # 19 down: 22 down minus ninety-four
    linear(1, "D20", 1, "A20", -9)           # 20 down: 20 across minus nine
    linear(1, "D21", 1, "A25", -52)          # 21 down: 25 across minus fifty-two
    linear(1, "D22", 6, "D20", 0)            # 22 down: 20 down times six
    linear(1, "D26", 5, "A24", 0)            # 26 down: five times 24 across
    linear(1, "D28", 1, "D21", 27)           # 28 down: 21 down plus twenty-seven

    return cnf, {"M": M}


if __name__ == "__main__":
    import numpy as np
    from pysat.solvers import Solver

    formula, outputs = create_model({})

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

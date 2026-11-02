# csplib_021_crossfigures: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_021_crossfigures.py

from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def digits_of(n):
    """The decimal digits of n, from left to right."""
    return [int(ch) for ch in str(n)]


def create_model(instance):
    """Fill a 9 by 9 crossfigure with digits so that every across and down answer is a
    number that matches its clue. Black cells show 0."""
    # The grid, one string per row. X is a black cell, _ a white cell without a clue
    # number, and a number a white cell that starts the answer with that clue number.
    grid = ["1 2 _ 3 X 4 _ 5 6",
            "7 _ X 8 _ _ X 9 _",
            "_ X 10 _ X 11 12 X _",
            "13 14 _ _ X 15 _ 16 _",
            "X _ X X X X X _ X",
            "17 _ 18 19 X 20 21 _ 22",
            "_ X 23 _ X 24 _ X _",
            "25 26 X 27 _ _ X 28 _",
            "29 _ _ _ X 30 _ _ _"]
    n_rows = len(grid)
    n_cols = len(grid[0].split())

    # cell_bits[(r, c)] holds the digit of white cell (r, c) as four values, least
    # significant first.
    cell_bits = {}
    for r in range(n_rows):
        for c in range(n_cols):
            if grid[r].split()[c] != "X":
                cell_bits[(r, c)] = [Bool(f"digit_{r}_{c}_{k}") for k in range(4)]

    constraints = []

    def digit(cell):
        """The digit of a white cell, as an integer expression."""
        return sum((2 ** k) * cell_bits[cell][k] for k in range(4))

    def spells(cells, n):
        """True when the cells hold the digits of n, from left to right."""
        terms = []
        for cell, d in zip(cells, digits_of(n)):
            for k in range(4):
                bit = cell_bits[cell][k]
                terms.append(bit if (d >> k) & 1 else ~bit)
        return And(terms)

    def number(cells):
        """The number the cells spell, read from left to right."""
        return sum(10 ** (len(cells) - 1 - k) * digit(cell) for k, cell in enumerate(cells))

    def answer_cells(is_across):
        """The white cells of each across or down answer, by clue number."""
        found = {}
        for r in range(n_rows):
            for c in range(n_cols):
                token = grid[r].split()[c]
                if token == "X":
                    continue
                # an answer starts at a white cell with no white cell before it
                before = (r, c - 1) if is_across else (r - 1, c)
                if before in cell_bits:
                    continue
                cells = []
                rr, cc = r, c
                while rr < n_rows and cc < n_cols and (rr, cc) in cell_bits:
                    cells.append((rr, cc))
                    if is_across:
                        cc += 1
                    else:
                        rr += 1
                if len(cells) >= 2:
                    found[int(token)] = cells
        return found

    # The white cells of each across and down answer, by clue number.
    across_cells = answer_cells(True)
    down_cells = answer_cells(False)

    # across[k] and down[k] are the numbers in the across and down answers with clue k.
    across = {k: number(cells) for k, cells in across_cells.items()}
    down = {k: number(cells) for k, cells in down_cells.items()}

    # Each white cell holds a digit from 0 to 9.
    for cell in cell_bits:
        constraints.append(digit(cell) <= 9)

    # The two-digit prime numbers, the two-digit square numbers and the four-digit
    # square numbers.
    primes = [p for p in range(10, 100) if is_prime(p)]
    squares2 = [s * s for s in range(4, 10)]
    squares4 = [s * s for s in range(32, 100)]

    # Across clues
    constraints.append(across[1] == 2 * across[27])           # 27 across times two
    constraints.append(across[4] == down[4] + 71)             # 4 down plus seventy-one
    constraints.append(across[7] == down[18] + 4)             # 18 down plus four
    constraints.append(16 * across[8] == down[6])             # 6 down divided by sixteen
    constraints.append(across[9] == down[2] - 18)             # 2 down minus eighteen
    constraints.append(across[10] == 6 * 144 // 12)           # a dozen in six gross
    constraints.append(across[11] == down[5] - 70)            # 5 down minus seventy

    # 23 across is a two-digit prime.
    constraints.append(Or([spells(across_cells[23], p) for p in primes]))
    # 13 across: 26 down times 23 across.
    for p in primes:
        constraints.append(If(spells(across_cells[23], p), across[13] == p * down[26]))
    constraints.append(across[15] == down[6] - 350)           # 6 down minus 350
    # 17 across: 25 across times 23 across.
    for p in primes:
        constraints.append(If(spells(across_cells[23], p), across[17] == p * across[25]))

    # 20 across is a four-digit square number.
    constraints.append(Or([spells(across_cells[20], s) for s in squares4]))
    # 24 across is a two-digit square number.
    constraints.append(Or([spells(across_cells[24], s) for s in squares2]))

    constraints.append(17 * across[25] == across[20])         # 20 across divided by seventeen
    constraints.append(4 * across[27] == down[6])             # 6 down divided by four
    constraints.append(across[28] == 4 * 12)                  # four dozen
    constraints.append(across[29] == 7 * 144)                 # seven gross
    constraints.append(across[30] == down[22] + 450)          # 22 down plus 450

    # Down clues
    constraints.append(down[1] == across[1] + 27)             # 1 across plus twenty-seven
    constraints.append(down[2] == 5 * 12)                     # five dozen
    constraints.append(down[3] == across[30] + 888)           # 30 across plus 888
    constraints.append(down[4] == 2 * across[17])             # two times 17 across
    constraints.append(12 * down[5] == across[29])            # 29 across divided by twelve
    constraints.append(down[6] == 4 * 12 * across[23])        # 28 across, four dozen, times 23 across
    constraints.append(down[10] == across[10] + 4)            # 10 across plus four
    constraints.append(down[12] == 3 * across[24])            # three times 24 across
    constraints.append(16 * down[14] == across[13])           # 13 across divided by sixteen
    constraints.append(down[16] == 15 * down[28])             # 28 down times fifteen
    constraints.append(down[17] == across[13] - 399)          # 13 across minus 399
    constraints.append(18 * down[18] == across[29])           # 29 across divided by eighteen
    constraints.append(down[19] == down[22] - 94)             # 22 down minus ninety-four
    constraints.append(down[20] == across[20] - 9)            # 20 across minus nine
    constraints.append(down[21] == across[25] - 52)           # 25 across minus fifty-two
    constraints.append(down[22] == 6 * down[20])              # 20 down times six
    constraints.append(down[26] == 5 * across[24])            # five times 24 across
    constraints.append(down[28] == down[21] + 27)             # 21 down plus twenty-seven

    # M[r][c] is the digit in row r, column c, or 0 for a black cell.
    M = [[digit((r, c)) if (r, c) in cell_bits else 0 for c in range(n_cols)]
         for r in range(n_rows)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"M": M}


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

# csplib_021_crossfigures: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python csplib_021_crossfigures.py

import math

from pyscipopt import Model, quicksum

# The grid of the statement, one string per row. "X" is a black cell, "_" an empty
# white cell, and a number is the label of the cell where an answer starts.
GRID = [
    "1 2 _ 3 X 4 _ 5 6",
    "7 _ X 8 _ _ X 9 _",
    "_ X 10 _ X 11 12 X _",
    "13 14 _ _ X 15 _ 16 _",
    "X _ X X X X X _ X",
    "17 _ 18 19 X 20 21 _ 22",
    "_ X 23 _ X 24 _ X _",
    "25 26 X 27 _ _ X 28 _",
    "29 _ _ _ X 30 _ _ _",
]


def is_prime(n):
    """True when n is a prime number: at least 2, with no divisor from 2 up to its square root."""
    return n >= 2 and all(n % d for d in range(2, math.isqrt(n) + 1))


def create_model(instance):
    """Crossfigures: fill the white cells of the grid with digits so that every clue holds.

    A white cell holds one digit. The digits of a run of white cells, read left to right
    for an across answer or top to bottom for a down answer, form a number, and that number
    is the answer to the clue numbered with the run's first cell. Each clue of the statement
    is written here as an equation between answers. The output M is the grid of digits,
    with 0 in the black cells.

    The instance file is empty ([]): the grid and the clues are fixed by the statement,
    so the argument is not read.
    """
    rows = [line.split() for line in GRID]  # rows[r][c]: the token in row r, column c
    n_rows, n_cols = len(rows), len(rows[0])
    # where[k]: the (row, column) of the cell labelled k
    where = {int(tok): (r, c) for r, row in enumerate(rows) for c, tok in enumerate(row) if tok.isdigit()}

    model = Model("csplib_021_crossfigures")

    # M[r, c] is the digit in row r, column c. A white cell holds one decimal digit, 0 to 9
    # (0 is needed: the clues force 8220 as the answer to 3 down). The upper bound of 0 holds
    # each black cell at 0, which is how the output shows it.
    M = model.addMatrixVar(
        (n_rows, n_cols),
        vtype="I",
        lb=0,
        ub=[[0 if tok == "X" else 9 for tok in row] for row in rows],
        name="M",
    )

    def read_answer(r, c, dr, dc):
        """The white cells from (r, c), stepping by (dr, dc), up to a black cell or the edge."""
        cells = []
        while r < n_rows and c < n_cols and rows[r][c] != "X":
            cells.append((r, c))
            r, c = r + dr, c + dc
        return cells

    def number(cells):
        """The number the cells spell, read in order: the first cell is the leading digit."""
        return quicksum(10 ** (len(cells) - 1 - i) * M[r, c] for i, (r, c) in enumerate(cells))

    def one_of(value, candidates, name):
        """Constrain value to be one of the candidates: one binary per candidate, exactly one set.

        SCIP has no prime or square constraint, so a clue that asks for one lists the values
        it may take.
        """
        pick = {v: model.addVar(name=f"{name}_{v}", vtype="B") for v in candidates}  # pick[v] is 1 when v is the answer
        model.addCons(quicksum(pick.values()) == 1)  # exactly one candidate is the answer
        model.addCons(value == quicksum(v * b for v, b in pick.items()))

    # across[k] (down[k]) is the number of the answer that starts at the cell labelled k.
    # An across answer starts where the cell to its left is black or off the grid; a down
    # answer where the cell above it is.
    across, down = {}, {}
    for k, (r, c) in where.items():
        if c == 0 or rows[r][c - 1] == "X":
            across[k] = number(read_answer(r, c, 0, 1))
        if r == 0 or rows[r - 1][c] == "X":
            down[k] = number(read_answer(r, c, 1, 0))

    # 23 across: a prime number. Its digits are the cells of the run, so the answer is below
    # 10 to the power of the run's cell count.
    limit = 10 ** len(read_answer(*where[23], 0, 1))
    one_of(across[23], [p for p in range(limit) if is_prime(p)], "prime_23")

    # 20 across and 24 across: square numbers. The positive squares below the limit are
    # listed; 0 is left out, an assumption (the statement does not say whether 0 is square).
    limit = 10 ** len(read_answer(*where[20], 0, 1))
    one_of(across[20], [v for v in range(1, limit) if math.isqrt(v) ** 2 == v], "square_20")
    limit = 10 ** len(read_answer(*where[24], 0, 1))
    one_of(across[24], [v for v in range(1, limit) if math.isqrt(v) ** 2 == v], "square_24")

    # Across clues. The products of two answers (13, 17 across; 6 down) are nonlinear,
    # since both factors are answers that vary; SCIP takes them as they are.
    model.addCons(across[1] == 2 * across[27])  # 1 across: 27 across times two
    model.addCons(across[4] == down[4] + 71)  # 4 across: 4 down plus seventy-one
    model.addCons(across[7] == down[18] + 4)  # 7 across: 18 down plus four
    model.addCons(16 * across[8] == down[6])  # 8 across: 6 down divided by sixteen
    model.addCons(across[9] == down[2] - 18)  # 9 across: 2 down minus eighteen
    model.addCons(across[10] == 72)  # 10 across: dozen in six gross, 6 * 144 / 12
    model.addCons(across[11] == down[5] - 70)  # 11 across: 5 down minus seventy
    model.addCons(across[13] == down[26] * across[23])  # 13 across: 26 down times 23 across
    model.addCons(across[15] == down[6] - 350)  # 15 across: 6 down minus 350
    model.addCons(across[17] == across[25] * across[23])  # 17 across: 25 across times 23 across
    model.addCons(17 * across[25] == across[20])  # 25 across: 20 across divided by seventeen
    model.addCons(4 * across[27] == down[6])  # 27 across: 6 down divided by four
    model.addCons(across[28] == 48)  # 28 across: four dozen
    model.addCons(across[29] == 1008)  # 29 across: seven gross, 7 * 144
    model.addCons(across[30] == down[22] + 450)  # 30 across: 22 down plus 450

    # Down clues
    model.addCons(down[1] == across[1] + 27)  # 1 down: 1 across plus twenty-seven
    model.addCons(down[2] == 60)  # 2 down: five dozen
    model.addCons(down[3] == across[30] + 888)  # 3 down: 30 across plus 888
    model.addCons(down[4] == 2 * across[17])  # 4 down: two times 17 across
    model.addCons(12 * down[5] == across[29])  # 5 down: 29 across divided by twelve
    model.addCons(down[6] == across[28] * across[23])  # 6 down: 28 across times 23 across
    model.addCons(down[10] == across[10] + 4)  # 10 down: 10 across plus four
    model.addCons(down[12] == 3 * across[24])  # 12 down: three times 24 across
    model.addCons(16 * down[14] == across[13])  # 14 down: 13 across divided by sixteen
    model.addCons(down[16] == 15 * down[28])  # 16 down: 28 down times fifteen
    model.addCons(down[17] == across[13] - 399)  # 17 down: 13 across minus 399
    model.addCons(18 * down[18] == across[29])  # 18 down: 29 across divided by eighteen
    model.addCons(down[19] == down[22] - 94)  # 19 down: 22 down minus ninety-four
    model.addCons(down[20] == across[20] - 9)  # 20 down: 20 across minus nine
    model.addCons(down[21] == across[25] - 52)  # 21 down: 25 across minus fifty-two
    model.addCons(down[22] == 6 * down[20])  # 22 down: 20 down times six
    model.addCons(down[26] == 5 * across[24])  # 26 down: five times 24 across
    model.addCons(down[28] == down[21] + 27)  # 28 down: 21 down plus twenty-seven

    return model, {"M": M}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

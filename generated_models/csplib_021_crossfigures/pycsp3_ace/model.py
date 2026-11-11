# csplib_021_crossfigures: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python csplib_021_crossfigures.py

from pycsp3 import *


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: a grid with black cells and numbered
    clues, each asking for a number. Fill every cell that is not black with a digit so that every
    clue holds: an answer is the number its cells spell, read across from left to right or down from
    top to bottom."""
    base = 10                       # the digits are 0 to 9
    dozen = 12                      # the clues measure in dozens and gross
    gross = 12 * dozen              # a gross is twelve dozen

    # The grid of the problem, a constant: row by row, a number is the clue number of an answer starting
    # in that cell, "_" is a cell to fill and X a black cell.
    grid = [
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
    rows = [line.split() for line in grid]
    n_rows = len(rows)
    n_cols = len(rows[0])

    def run_from(r, c, dr, dc):
        # the cells from (r, c) in direction (dr, dc) up to a black cell or the edge
        found = []
        while r < n_rows and c < n_cols and rows[r][c] != "X":
            found.append((r, c))
            r, c = r + dr, c + dc
        return found

    def answers(dr, dc):
        # {clue number: cells of its run} for the answers read in direction (dr, dc); an answer starts at a
        # clue cell whose previous cell in that direction is black or off the grid
        found = {}
        for r in range(n_rows):
            for c in range(n_cols):
                starts = not (r - dr >= 0 and c - dc >= 0 and rows[r - dr][c - dc] != "X")
                if rows[r][c].isdigit() and starts:
                    run = run_from(r, c, dr, dc)
                    # a single cell carries no clue, so it is only constrained by the other direction
                    if len(run) > 1:
                        found[int(rows[r][c])] = run
        return found

    across_runs = answers(0, 1)
    down_runs = answers(1, 0)

    # cells[r][c] is the digit in row r, column c, counted from 0. A cell may hold 0, including the first digit
    # of an answer: the statement only says a digit may be 0, so this is a reading.
    cells = VarArray(size=[n_rows, n_cols], dom=range(base))

    # across_answers[n] is the number read across the answer with clue n, with one digit per cell of its run
    # (leading zeros allowed, as for the digits above).
    across_answers = {
        label: Var(id=f"across_{label}", dom=range(base ** len(run)))
        for label, run in across_runs.items()
    }
    # down_answers[n] is the number read down the answer with clue n, likewise.
    down_answers = {
        label: Var(id=f"down_{label}", dom=range(base ** len(run)))
        for label, run in down_runs.items()
    }

    def squares(n_digits):
        # the squares of at most n_digits digits, 0 included
        return {v for v in range(base ** n_digits) if round(v ** 0.5) ** 2 == v}

    def primes(n_digits):
        # the primes of at most n_digits digits
        return {v for v in range(2, base ** n_digits) if all(v % p for p in range(2, v))}

    satisfy(
        # each cell marked X holds 0
        cells[r][c] == 0 for r in range(n_rows) for c in range(n_cols) if rows[r][c] == "X"
    )

    satisfy(
        # each across answer, read as a number, equals the digits of its run, leftmost digit first
        across_answers[label] == Sum(cells[r][c] * base ** (len(run) - 1 - j) for j, (r, c) in enumerate(run))
        for label, run in across_runs.items()
    )

    satisfy(
        # each down answer, read as a number, equals the digits of its run, topmost digit first
        down_answers[label] == Sum(cells[r][c] * base ** (len(run) - 1 - j) for j, (r, c) in enumerate(run))
        for label, run in down_runs.items()
    )

    satisfy(
        # 1 across: 27 across times two
        across_answers[1] == 2 * across_answers[27],
        # 4 across: 4 down plus seventy-one
        across_answers[4] == down_answers[4] + 71,
        # 7 across: 18 down plus four
        across_answers[7] == down_answers[18] + 4,
        # 8 across: 6 down divided by sixteen, so 6 down is sixteen times 8 across
        down_answers[6] == 16 * across_answers[8],
        # 9 across: 2 down minus eighteen
        across_answers[9] == down_answers[2] - 18,
        # 10 across: the number of dozens in six gross
        across_answers[10] == 6 * gross // dozen,
        # 11 across: 5 down minus seventy
        across_answers[11] == down_answers[5] - 70,
        # 13 across: 26 down times 23 across
        across_answers[13] == down_answers[26] * across_answers[23],
        # 15 across: 6 down minus 350
        across_answers[15] == down_answers[6] - 350,
        # 17 across: 25 across times 23 across
        across_answers[17] == across_answers[25] * across_answers[23],
        # 20 across: a square number
        across_answers[20] in squares(len(across_runs[20])),
        # 23 across: a prime number
        across_answers[23] in primes(len(across_runs[23])),
        # 24 across: a square number
        across_answers[24] in squares(len(across_runs[24])),
        # 25 across: 20 across divided by seventeen, so 20 across is seventeen times 25 across
        across_answers[20] == 17 * across_answers[25],
        # 27 across: 6 down divided by four, so 6 down is four times 27 across
        down_answers[6] == 4 * across_answers[27],
        # 28 across: four dozen
        across_answers[28] == 4 * dozen,
        # 29 across: seven gross
        across_answers[29] == 7 * gross,
        # 30 across: 22 down plus 450
        across_answers[30] == down_answers[22] + 450,
    )

    satisfy(
        # 1 down: 1 across plus twenty-seven
        down_answers[1] == across_answers[1] + 27,
        # 2 down: five dozen
        down_answers[2] == 5 * dozen,
        # 3 down: 30 across plus 888
        down_answers[3] == across_answers[30] + 888,
        # 4 down: two times 17 across
        down_answers[4] == 2 * across_answers[17],
        # 5 down: 29 across divided by twelve, so 29 across is twelve times 5 down
        across_answers[29] == 12 * down_answers[5],
        # 6 down: 28 across times 23 across
        down_answers[6] == across_answers[28] * across_answers[23],
        # 10 down: 10 across plus four
        down_answers[10] == across_answers[10] + 4,
        # 12 down: three times 24 across
        down_answers[12] == 3 * across_answers[24],
        # 14 down: 13 across divided by sixteen, so 13 across is sixteen times 14 down
        across_answers[13] == 16 * down_answers[14],
        # 16 down: 28 down times fifteen
        down_answers[16] == 15 * down_answers[28],
        # 17 down: 13 across minus 399
        down_answers[17] == across_answers[13] - 399,
        # 18 down: 29 across divided by eighteen, so 29 across is eighteen times 18 down
        across_answers[29] == 18 * down_answers[18],
        # 19 down: 22 down minus ninety-four
        down_answers[19] == down_answers[22] - 94,
        # 20 down: 20 across minus nine
        down_answers[20] == across_answers[20] - 9,
        # 21 down: 25 across minus fifty-two
        down_answers[21] == across_answers[25] - 52,
        # 22 down: 20 down times six
        down_answers[22] == 6 * down_answers[20],
        # 26 down: five times 24 across
        down_answers[26] == 5 * across_answers[24],
        # 28 down: 21 down plus twenty-seven
        down_answers[28] == down_answers[21] + 27,
    )

    return {"M": cells}


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variables in outputs.items():
            print(name, "=", values(variables))
    else:
        print("No solution:", status())

# csplib_021_crossfigures: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_021_crossfigures.html
# Run it (after `pip install mip numpy`) with:
#   python csplib_021_crossfigures.py

import mip


def create_model(instance):
    """Crossfigures are the numerical equivalent of crosswords: fill a 9 by 9 grid with
    digits so that every across and down entry is a number that meets its clue, such
    as "27 across times two", "a prime number" or "a square number"."""
    # The puzzle grid. A number marks the first cell of a clue, _ is an empty cell to
    # fill, and X is a black cell.
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
    n_side = len(rows)  # the grid is n_side cells wide and high
    DOZEN = 12  # the number of items in a dozen
    GROSS = 144  # the number of items in a gross, which is twelve dozen

    # The cells of each entry, from its first cell on, keyed by clue: A for across, D for down.
    entries = {}
    for r in range(n_side):
        c = 0
        while c < n_side:
            if rows[r][c] == "X":
                c += 1
                continue
            start = c
            while c < n_side and rows[r][c] != "X":
                c += 1
            if c - start >= 2:
                entries[f"A{rows[r][start]}"] = [(r, k) for k in range(start, c)]
    for c in range(n_side):
        r = 0
        while r < n_side:
            if rows[r][c] == "X":
                r += 1
                continue
            start = r
            while r < n_side and rows[r][c] != "X":
                r += 1
            if r - start >= 2:
                entries[f"D{rows[start][c]}"] = [(k, c) for k in range(start, r)]

    model = mip.Model(solver_name="CBC")

    # The empty cells, each of which holds a digit.
    empty = {(r, c) for r in range(n_side) for c in range(n_side) if rows[r][c] != "X"}

    # digit[(r, c)] is the digit in row r, column c, from 0 to 9
    digit = {(r, c): model.add_var(f"digit_{r}_{c}", var_type=mip.INTEGER, lb=0, ub=9)
             for (r, c) in sorted(empty)}

    # The number an entry spells, reading its cells from the first, which holds the leading digit.
    def val(key):
        cells = entries[key]
        return mip.xsum(10 ** (len(cells) - 1 - k) * digit[cell] for k, cell in enumerate(cells))

    # The smallest and largest numbers with as many digits as the entry.
    def digit_range(key):
        length = len(entries[key])
        return 10 ** (length - 1), 10 ** length - 1

    # True when p is a prime number.
    def is_prime(p):
        return p > 1 and all(p % q for q in range(2, int(p ** 0.5) + 1))

    # A choice from candidates: each candidate gets a choice variable, and exactly one is picked.
    # Returns the choice variables and the number picked.
    def choose(candidates, label):
        picks = [model.add_var(f"{label}_{i}", var_type=mip.BINARY) for i in range(len(candidates))]
        model.add_constr(mip.xsum(picks) == 1)
        return picks, mip.xsum(c * pick for c, pick in zip(candidates, picks))

    # x times the candidate that is picked, for x between lo and hi.
    def product_with_pick(x, lo, hi, picks, candidates, label):
        terms = []
        for i, (c, pick) in enumerate(zip(candidates, picks)):
            # y is x when this candidate is picked, and 0 otherwise.
            y = model.add_var(f"{label}_{i}", lb=0, ub=hi)
            model.add_constr(y <= hi * pick)
            model.add_constr(y >= lo * pick)
            model.add_constr(y <= x - lo * (1 - pick))
            model.add_constr(y >= x - hi * (1 - pick))
            terms.append(c * y)
        return mip.xsum(terms)

    # An entry is a number written without a leading zero.
    for cells in entries.values():
        model.add_constr(digit[cells[0]] >= 1)

    # Two-digit primes, two-digit squares and four-digit squares.
    primes2 = [p for p in range(10, 100) if is_prime(p)]
    squares2 = [k * k for k in range(1, 100) if 10 <= k * k < 100]
    squares4 = [k * k for k in range(1, 100) if 1000 <= k * k < 10000]

    # 23 across: a prime number
    picks23, prime23 = choose(primes2, "prime23")
    model.add_constr(val("A23") == prime23)

    # 20 across: a square number
    picks20, square20 = choose(squares4, "square20")
    model.add_constr(val("A20") == square20)

    # 24 across: a square number
    picks24, square24 = choose(squares2, "square24")
    model.add_constr(val("A24") == square24)

    # 13 across: 26 down times 23 across
    lo26, hi26 = digit_range("D26")
    model.add_constr(val("A13") == product_with_pick(val("D26"), lo26, hi26, picks23, primes2, "p13"))

    # 17 across: 25 across times 23 across
    lo25, hi25 = digit_range("A25")
    model.add_constr(val("A17") == product_with_pick(val("A25"), lo25, hi25, picks23, primes2, "p17"))

    # The across clues.
    model.add_constr(val("A1") == 2 * val("A27"))           # 27 across times two
    model.add_constr(val("A4") == val("D4") + 71)           # 4 down plus seventy-one
    model.add_constr(val("A7") == val("D18") + 4)           # 18 down plus four
    model.add_constr(16 * val("A8") == val("D6"))           # 6 down divided by sixteen
    model.add_constr(val("A9") == val("D2") - 18)           # 2 down minus eighteen
    model.add_constr(val("A10") == 6 * GROSS // DOZEN)      # dozen in six gross
    model.add_constr(val("A11") == val("D5") - 70)          # 5 down minus seventy
    model.add_constr(val("A15") == val("D6") - 350)         # 6 down minus 350
    model.add_constr(17 * val("A25") == val("A20"))         # 20 across divided by seventeen
    model.add_constr(4 * val("A27") == val("D6"))           # 6 down divided by four
    model.add_constr(val("A28") == 4 * DOZEN)               # four dozen
    model.add_constr(val("A29") == 7 * GROSS)               # seven gross
    model.add_constr(val("A30") == val("D22") + 450)        # 22 down plus 450

    # The down clues.
    model.add_constr(val("D1") == val("A1") + 27)           # 1 across plus twenty-seven
    model.add_constr(val("D2") == 5 * DOZEN)                # five dozen
    model.add_constr(val("D3") == val("A30") + 888)         # 30 across plus 888
    model.add_constr(val("D4") == 2 * val("A17"))           # two times 17 across
    model.add_constr(12 * val("D5") == val("A29"))          # 29 across divided by twelve
    model.add_constr(val("D6") == 4 * DOZEN * val("A23"))   # 28 across times 23 across, 28 across being four dozen
    model.add_constr(val("D10") == val("A10") + 4)          # 10 across plus four
    model.add_constr(val("D12") == 3 * val("A24"))          # three times 24 across
    model.add_constr(16 * val("D14") == val("A13"))         # 13 across divided by sixteen
    model.add_constr(val("D16") == 15 * val("D28"))         # 28 down times fifteen
    model.add_constr(val("D17") == val("A13") - 399)        # 13 across minus 399
    model.add_constr(18 * val("D18") == val("A29"))         # 29 across divided by eighteen
    model.add_constr(val("D19") == val("D22") - 94)         # 22 down minus ninety-four
    model.add_constr(val("D20") == val("A20") - 9)          # 20 across minus nine
    model.add_constr(val("D21") == val("A25") - 52)         # 25 across minus fifty-two
    model.add_constr(val("D22") == 6 * val("D20"))          # 20 down times six
    model.add_constr(val("D26") == 5 * val("A24"))          # five times 24 across
    model.add_constr(val("D28") == val("D21") + 27)         # 21 down plus twenty-seven

    # M[r][c] is the digit in row r, column c. A black cell holds no digit, so its entry is a variable fixed at 0.
    M = []
    for r in range(n_side):
        row = []
        for c in range(n_side):
            if (r, c) in digit:
                row.append(digit[(r, c)])
            else:
                row.append(model.add_var(f"black_{r}_{c}", lb=0, ub=0, var_type=mip.INTEGER))
        M.append(row)

    return model, {"M": M}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

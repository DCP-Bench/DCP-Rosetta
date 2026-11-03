# send_more_money: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Run it (after `pip install hermax`) with:
#   python send_more_money.py
from hermax.model import Model


def create_model(instance):
    """SEND + MORE = MONEY: assign each of the letters s, e, n, d, m, o, r, y a
    different digit from 0 to 9, with no leading zero in SEND, MORE or MONEY,
    so that the addition SEND + MORE = MONEY holds when each word is read as a number.
    The puzzle is fixed by the problem statement; the instance carries no data."""
    # The instance has no fields: every number below comes from the puzzle itself.
    m = Model()

    # Decision variables: one digit per letter, 0..9.
    # s, e, n, d are the letters of SEND; m_, o, r, y those of MORE and MONEY.
    s = m.int("s", 0, 9)  # the digit of S
    e = m.int("e", 0, 9)  # the digit of E
    n = m.int("n", 0, 9)  # the digit of N
    d = m.int("d", 0, 9)  # the digit of D
    m_ = m.int("m", 0, 9)  # the digit of M
    o = m.int("o", 0, 9)  # the digit of O
    r = m.int("r", 0, 9)  # the digit of R
    y = m.int("y", 0, 9)  # the digit of Y
    letters = [s, e, n, d, m_, o, r, y]

    # Every letter stands for a different digit.
    m &= m.vector(letters).all_different()

    # No word starts with zero: SEND starts with S, MORE and MONEY with M.
    m &= (s != 0)
    m &= (m_ != 0)

    # SEND + MORE = MONEY, each word read as a number.
    # E is the hundreds digit of SEND, the units digit of MORE and the tens digit of MONEY.
    m &= (1000 * s + 100 * e + 10 * n + d + 1000 * m_ + 100 * o + 10 * r + e
          == 10000 * m_ + 1000 * o + 100 * n + 10 * e + y)

    # No objective: any assignment that meets the constraints answers the puzzle.
    return m, {"s": s, "e": e, "n": n, "d": d, "m": m_, "o": o, "r": r, "y": y}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

# session1_bank_card: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Run it (after `pip install hermax`) with:
#   python session1_bank_card.py

from hermax.model import Model


def create_model(instance):
    """My bank card has a 4-digit PIN abcd. No two digits are the same, the two-digit
    number cd is three times the two-digit number ab, and the two-digit number da is two
    times the two-digit number bc. Find the PIN (a, b, c, d)."""
    # The instance is empty: the statement fixes all the data, so nothing is read from it.

    m = Model()

    # a, b, c, d: the four digits of the PIN, each a digit from 0 to 9
    a, b, c, d = (m.int(name, 0, 9) for name in "abcd")

    # No two digits of the PIN are the same.
    m &= m.vector([a, b, c, d]).all_different()
    # The two-digit number cd (10*c + d) is three times the two-digit number ab (10*a + b).
    m &= (10 * c + d == 30 * a + 3 * b)
    # The two-digit number da (10*d + a) is two times the two-digit number bc (10*b + c).
    m &= (10 * d + a == 20 * b + 2 * c)

    # There is no objective: any PIN that meets the three facts is an answer.
    return m, {"a": a, "b": b, "c": c, "d": d}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

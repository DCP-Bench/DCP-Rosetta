# hanging_weights: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Run it (after `pip install hermax`) with:
#   python hanging_weights.py

from hermax.model import Model


def create_model(instance):
    """Give each of the thirteen weights A to M, hanging from a system of bars, an integer
    value from 1 to 13, so that the diagram balances: on every bar, the weights on either
    side of its pivot, weighted by their distance from the pivot, are equal, and a bar
    hanging beneath another contributes its total weight as one single weight.
    The puzzle has no objective: any balancing assignment is an answer."""
    # The instance has no fields: the puzzle's data are fixed by its statement.

    m = Model()

    # Each weight is an integer from 1 to 13 (the range the statement gives).
    # a..m are the weights A..M of the diagram, in the statement's letters.
    a = m.int("a", 1, 13)
    b = m.int("b", 1, 13)
    c = m.int("c", 1, 13)
    d = m.int("d", 1, 13)
    e = m.int("e", 1, 13)
    f = m.int("f", 1, 13)
    g = m.int("g", 1, 13)
    h = m.int("h", 1, 13)
    i = m.int("i", 1, 13)
    j = m.int("j", 1, 13)
    k = m.int("k", 1, 13)
    l = m.int("l", 1, 13)
    m_ = m.int("m", 1, 13)

    # Bottom-right bar: C and D balance, 5*C = D.
    m &= (5 * c == d)
    # The bar above it: G balances the bar carrying C and D, 3*G = 2*(C+D).
    m &= (3 * g == 2 * (c + d))
    # The bar carrying A and B: 4*A = B.
    m &= (4 * a == b)
    # The bar carrying E and F: 3*E = 2*F.
    m &= (3 * e == 2 * f)
    # The H bar: 3*H = 2*(E+F) + 3*I, where the E-F bar hangs beneath it.
    m &= (3 * h == 2 * (e + f) + 3 * i)
    # The L-M bar: the sub-bar carrying H, I and the E-F bar (weight H+I+E+F) at 1,
    # L at 1 and M at 4, so (H+I+E+F) = L + 4*M.
    m &= (h + i + e + f == l + 4 * m_)
    # The J-K bar: the A-B bar at 3, J at 2 on one side; K at 1 and the G-C-D bar at 2
    # on the other, so 3*(A+B) + 2*J = K + 2*(G+C+D).
    m &= (3 * (a + b) + 2 * j == k + 2 * (g + c + d))
    # The top bar: the L-M bar (H+I+E+F+L+M) at 4 and the J-K bar
    # (J+K+A+B+G+C+D) at 3, so 4*(H+I+E+F+L+M) = 3*(J+K+A+B+G+C+D).
    m &= (4 * (h + i + e + f + l + m_) == 3 * (j + k + a + b + g + c + d))

    # The answer is the value of each weight, A to M, reported under its letter.
    outputs = {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
               "h": h, "i": i, "j": j, "k": k, "l": l, "m": m_}
    return m, outputs


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

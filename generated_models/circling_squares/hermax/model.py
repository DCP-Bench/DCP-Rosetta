# circling_squares: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install hermax`) with:
#   python circling_squares.py

from hermax.model import Model


def create_model(instance):
    """Circling the squares (Dudeney): place ten different whole numbers A, B, C, D, E, F, G, H, I, K
    round a circle so that the squares of any two adjacent numbers add up to the squares of the two
    numbers diametrically opposite them. A = 16, B = 2, F = 8 and G = 14 are given; find the other six.
    Fractions are not allowed and no number needs more than two figures, so every number is 1..99."""
    # The puzzle is fixed by its statement, so the instance carries no data (its field list is empty).
    # The squares around the circle, in order; the opposite of square p is square p + 5.
    circle = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
    # The four numbers the statement places as examples.
    given = {"A": 16, "B": 2, "F": 8, "G": 14}

    m = Model()

    # x[name] is the number placed in that square, a whole number from 1 to 99
    x = {name: m.int(name, 1, 99) for name in circle}

    # Every square holds a different number.
    m &= m.vector([x[name] for name in circle]).all_different()

    # The four numbers the statement places as examples stand as they are.
    for name, value in given.items():
        m &= (x[name] == value)

    def square(v):
        # hermax 1.3.0 does not support IntVar * IntVar, so v * v is written as a step function
        # with one step per value (v = 1 gives 1, v = t gives t * t, from the step at t on).
        return v.piecewise(base_value=1, steps={t: t * t for t in range(2, 100)})

    # Circle constraint, one per pair of adjacent squares: the sum of the squares of the two adjacent
    # numbers equals the sum of the squares of the two numbers opposite them. The five equations are
    # A,B against F,G; B,C against G,H; C,D against H,I; D,E against I,K; E,F against K,A.
    for p in range(5):
        a, b = circle[p], circle[(p + 1) % 10]
        c, d = circle[(p + 5) % 10], circle[(p + 6) % 10]
        m &= (square(x[a]) + square(x[b]) == square(x[c]) + square(x[d]))

    # Satisfaction problem: no objective.
    return m, {name: x[name] for name in circle}


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

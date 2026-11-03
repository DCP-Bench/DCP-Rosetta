# circling_squares: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Run it (after `pip install cpmpy`) with:
#   python circling_squares.py

import cpmpy as cp


def create_model(instance):
    """Circling the squares: place a different number in each of the ten squares
    of a circle so that the sum of the squares of any two adjacent numbers equals
    the sum of the squares of the two numbers diametrically opposite them."""
    n = 10  # squares in the circle, named A, B, C, D, E, F, G, H, I, K in order

    # x[j] is the number placed in square j; the puzzle says no number needs more than two figures
    x = cp.intvar(1, 99, shape=n, name="x")
    A, B, C, D, E, F, G, H, I, K = x

    model = cp.Model()

    # Each square holds a different number.
    model.add(cp.AllDifferent(x))

    # The four numbers given as examples stand as they are.
    model.add(A == 16)
    model.add(B == 2)
    model.add(F == 8)
    model.add(G == 14)

    # Two adjacent squares have the same sum of squares as the two squares opposite them.
    model.add(A**2 + B**2 == F**2 + G**2)
    model.add(B**2 + C**2 == G**2 + H**2)
    model.add(C**2 + D**2 == H**2 + I**2)
    model.add(D**2 + E**2 == I**2 + K**2)
    model.add(E**2 + F**2 == K**2 + A**2)

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E,
                   "F": F, "G": G, "H": H, "I": I, "K": K}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

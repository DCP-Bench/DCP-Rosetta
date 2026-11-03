# csplib_041_n_fractions: a hermax (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install hermax`) with:
#   python csplib_041_n_fractions.py
from itertools import permutations

from hermax.model import Model


def create_model(instance):
    """Find nine distinct non-zero digits A, B, ..., I with A/BC + D/EF + G/HI = 1, where
    BC, EF and HI are the two-digit numbers 10*B + C, 10*E + F and 10*H + I. The statement
    gives all the data, so the instance is empty and is not read."""
    names = "ABCDEFGHI"

    # The allowed combinations of the nine digits. Every candidate assignment is one
    # permutation of 1..9 (distinct and non-zero). The equation is multiplied through by
    # BC * EF * HI so that it holds in integer arithmetic, with no division:
    #   A * EF * HI + D * BC * HI + G * BC * EF == BC * EF * HI
    # hermax cannot multiply two integer variables (TypeError), and this cleared equation
    # has products of three of them, so the relation is enumerated here: 9! rows filtered
    # to the few that satisfy it, and the solver picks one row through a table constraint.
    rows = []
    for a, b, c, d, e, f, g, h, i in permutations(range(1, 10), 9):
        bc, ef, hi = 10 * b + c, 10 * e + f, 10 * h + i
        if a * ef * hi + d * bc * hi + g * bc * ef == bc * ef * hi:
            rows.append((a, b, c, d, e, f, g, h, i))

    m = Model()

    # digits[k]: the digit (1..9) that the letter names[k] stands for
    digits = [m.int(name, 1, 9) for name in names]

    # The nine digits are all different. The table rows already have this property,
    # but the statement asks for it, so it is stated here as well.
    m &= m.vector(digits).all_different()

    # (A, B, ..., I) is one of the allowed combinations, so the equation holds.
    m &= m.table(digits, allowed=rows)

    # No objective: the statement asks for the digits, not an optimum.
    return m, dict(zip(names, digits))


if __name__ == "__main__":
    model, outputs = create_model({})
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

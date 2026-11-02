# csplib_041_n_fractions: a cvc5 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install cvc5 numpy`) with:
#   python csplib_041_n_fractions.py

import cvc5.pythonic as c5


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    # The problem fixes all its data, so nothing is read from the instance.

    # The nine digits A to I
    A, B, C, D, E, F, G, H, I = digits = [c5.Int(name) for name in "ABCDEFGHI"]

    # The two-digit numbers BC, EF and HI
    BC = 10 * B + C
    EF = 10 * E + F
    HI = 10 * H + I

    # Facts that fix each product to its digit, collected as the products are made.
    product_facts = []

    def digit_times(name, digit, number):
        """A new number equal to the digit times the number."""
        p = c5.Int(name)
        product_facts.append(c5.Or([c5.And(digit == d, p == d * number) for d in range(1, 10)]))
        return p

    # EF * HI, BC * HI and BC * EF
    EF_HI = 10 * digit_times("E_HI", E, HI) + digit_times("F_HI", F, HI)
    BC_HI = 10 * digit_times("B_HI", B, HI) + digit_times("C_HI", C, HI)
    BC_EF = 10 * digit_times("B_EF", B, EF) + digit_times("C_EF", C, EF)

    # A / BC + D / EF + G / HI = 1, multiplied by BC * EF * HI:
    # A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI
    left = digit_times("A_EF_HI", A, EF_HI) + digit_times("D_BC_HI", D, BC_HI) + digit_times("G_BC_EF", G, BC_EF)
    right = 10 * digit_times("B_EF_HI", B, EF_HI) + digit_times("C_EF_HI", C, EF_HI)

    solver = c5.Solver()

    # Each digit is from 1 to 9.
    solver.add([d >= 1 for d in digits] + [d <= 9 for d in digits])

    # The nine digits are all different.
    solver.add(c5.Distinct(digits))

    # Each product is the digit times its number.
    solver.add(product_facts)

    # The fractions add up to 1.
    solver.add(left == right)

    return solver, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

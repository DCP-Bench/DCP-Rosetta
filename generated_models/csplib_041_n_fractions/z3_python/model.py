# csplib_041_n_fractions: a Z3 (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install z3-solver numpy`) with:
#   python csplib_041_n_fractions.py

import z3


def create_model(instance):
    """Find nine different non-zero digits A to I such that A / BC + D / EF + G / HI = 1,
    where BC, EF and HI are the two-digit numbers made of the digit pairs B C, E F and H I."""
    # The nine digits A to I, each from 1 to 9.
    A, B, C, D, E, F, G, H, I = digits = z3.Ints("A B C D E F G H I")
    solver = z3.Solver()

    solver.add([c for digit in digits for c in (digit >= 1, digit <= 9)])

    # The nine digits are all different.
    solver.add(z3.Distinct(digits))

    # The denominators BC, EF and HI, as two-digit numbers.
    BC, EF, HI = 10 * B + C, 10 * E + F, 10 * H + I

    # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI to avoid fractions.
    solver.add(A * EF * HI + D * BC * HI + G * BC * EF == BC * EF * HI)

    return solver, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}


if __name__ == "__main__":
    import numpy as np

    solver, outputs = create_model({})

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

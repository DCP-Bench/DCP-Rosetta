# csplib_041_n_fractions: a PyCSP3 model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install pycsp3`, which also needs Java for its ACE solver) with:
#   python csplib_041_n_fractions.py

from pycsp3 import *


def create_model(instance):
    """Find distinct non-zero digits such that A / BC + D / EF + G / HI = 1, where BC, EF and HI
    are the two-digit numbers formed by B and C, E and F, and H and I."""
    base = 10                                            # a two-digit number is base times its tens digit plus its units digit
    lowest_digit = 1                                     # the digits are non-zero
    min_two_digit = base * lowest_digit + lowest_digit   # 11, the smallest two-digit number with non-zero digits
    max_two_digit = base * base - 1                      # 99, the largest two-digit number with non-zero digits
    two_digits = range(min_two_digit, max_two_digit + 1)

    # A is the numerator of the first fraction, a digit.
    A = Var(dom=range(lowest_digit, base))
    # B is the tens digit of BC.
    B = Var(dom=range(lowest_digit, base))
    # C is the units digit of BC.
    C = Var(dom=range(lowest_digit, base))
    # D is the numerator of the second fraction, a digit.
    D = Var(dom=range(lowest_digit, base))
    # E is the tens digit of EF. It is named E_digit because E is a reserved identifier in ACE;
    # the dict key E is the output name.
    E_digit = Var(dom=range(lowest_digit, base))
    # F is the units digit of EF.
    F = Var(dom=range(lowest_digit, base))
    # G is the numerator of the third fraction, a digit.
    G = Var(dom=range(lowest_digit, base))
    # H is the tens digit of HI.
    H = Var(dom=range(lowest_digit, base))
    # I is the units digit of HI.
    I = Var(dom=range(lowest_digit, base))

    # bc is the denominator BC, a two-digit number.
    bc = Var(dom=two_digits)
    # ef is the denominator EF, a two-digit number.
    ef = Var(dom=two_digits)
    # hi is the denominator HI, a two-digit number.
    hi = Var(dom=two_digits)

    satisfy(
        # The nine digits are distinct.
        AllDifferent([A, B, C, D, E_digit, F, G, H, I]),
        # BC, EF and HI are the two-digit numbers formed by their digits.
        bc == base * B + C,
        ef == base * E_digit + F,
        hi == base * H + I,
        # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI.
        A * ef * hi + D * bc * hi + G * bc * ef == bc * ef * hi,
    )

    return {
        "A": A,
        "B": B,
        "C": C,
        "D": D,
        "E": E_digit,
        "F": F,
        "G": G,
        "H": H,
        "I": I,
    }


if __name__ == "__main__":
    outputs = create_model({})
    if solve() is SAT:
        for name, variable in outputs.items():
            print(name, "=", value(variable))
    else:
        print("No solution:", status())

# csplib_041_n_fractions: a CPMpy model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install cpmpy`) with:
#   python csplib_041_n_fractions.py

import cpmpy as cp


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    # The problem fixes all its data, so nothing is read from the instance.

    # x holds the digits A, B, C, D, E, F, G, H, I
    x = cp.intvar(1, 9, shape=9, name="x")
    A, B, C, D, E, F, G, H, I = x

    # The two-digit numbers BC, EF and HI
    den1 = cp.intvar(11, 99, name="BC")
    den2 = cp.intvar(11, 99, name="EF")
    den3 = cp.intvar(11, 99, name="HI")

    model = cp.Model()

    # The nine digits are all different.
    model.add(cp.AllDifferent(x))

    # BC, EF and HI are the numbers written with the digit pairs B C, E F and H I.
    model.add(den1 == 10 * B + C)
    model.add(den2 == 10 * E + F)
    model.add(den3 == 10 * H + I)

    # A / BC + D / EF + G / HI = 1, multiplied by the three denominators to stay in integers.
    model.add(A * den2 * den3 + D * den1 * den3 + G * den1 * den2 == den1 * den2 * den3)

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}


if __name__ == "__main__":
    model, outputs = create_model({})
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

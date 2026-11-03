# csplib_041_n_fractions: a SCIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install pyscipopt numpy`) with:
#   python csplib_041_n_fractions.py

import numpy as np
from pyscipopt import Model


def create_model(instance):
    """Find distinct non-zero digits A, B, C, D, E, F, G, H, I such that
    A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit
    numbers 10*B + C, 10*E + F and 10*H + I.

    The instance file is empty ([]), so the statement fixes all the data and
    `instance` is not read. The nine digits are distinct and non-zero, so they
    are exactly the digits 1 to 9, each used once.
    """
    model = Model("csplib_041_n_fractions")

    # x[s, d] = 1 when slot s holds digit d. The slots are, in order, A, B, C,
    # D, E, F, G, H, I, and the digits are 1 to 9 (row s, column d - 1).
    x = model.addMatrixVar((9, 9), vtype="B", name="x")

    # Every slot holds exactly one digit.
    model.addMatrixCons(x.sum(axis=1) == 1)
    # All different: each digit is used at most once. With nine slots and nine
    # digits, this makes every digit used exactly once. SCIP has no all-different
    # constraint, so it is written this way.
    model.addMatrixCons(x.sum(axis=0) <= 1)

    # The digit in each slot: A, B, ..., I are the d with x[s, d] = 1, so each
    # lies in 1 to 9.
    A, B, C, D, E, F, G, H, I = x @ np.arange(1, 10)

    # The two-digit numbers BC, EF and HI, each made from its tens and units
    # digit. Their bounds come from the digit range 1 to 9: the smallest is 11
    # (digits 1 and 1) and the largest is 99 (digits 9 and 9).
    BC = model.addVar(vtype="I", lb=11, ub=99, name="BC")
    EF = model.addVar(vtype="I", lb=11, ub=99, name="EF")
    HI = model.addVar(vtype="I", lb=11, ub=99, name="HI")
    model.addCons(BC == 10 * B + C)
    model.addCons(EF == 10 * E + F)
    model.addCons(HI == 10 * H + I)

    # A / BC + D / EF + G / HI = 1, with the three denominators cleared. Each
    # denominator is at least 11, so multiplying by BC * EF * HI keeps the
    # equation exact.
    model.addCons(A * EF * HI + D * BC * HI + G * BC * EF == BC * EF * HI)

    # The problem asks for the digits only, so there is no objective: any
    # assignment that satisfies the constraints above is an answer.

    outputs = {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

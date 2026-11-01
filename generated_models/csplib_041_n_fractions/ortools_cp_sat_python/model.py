# csplib_041_n_fractions: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install ortools`) with:
#   python csplib_041_n_fractions.py

from ortools.sat.python import cp_model


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    model = cp_model.CpModel()

    def times(x, y, upper, name):
        """A new variable equal to x * y, with the given upper bound."""
        p = model.new_int_var(0, upper, name)
        model.add_multiplication_equality(p, [x, y])
        return p

    # The nine digits A to I, each from 1 to 9.
    A, B, C, D, E, F, G, H, I = digits = [model.new_int_var(1, 9, name) for name in "ABCDEFGHI"]
    # All nine digits are different.
    model.add_all_different(digits)

    # BC, EF and HI are the two-digit numbers with tens digit B, E, H and units digit C, F, I.
    BC = model.new_int_var(11, 99, "BC")
    EF = model.new_int_var(11, 99, "EF")
    HI = model.new_int_var(11, 99, "HI")
    model.add(BC == 10 * B + C)
    model.add(EF == 10 * E + F)
    model.add(HI == 10 * H + I)

    # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI, gives
    # A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI.
    # The products are built two factors at a time.
    BC_EF = times(BC, EF, 99 * 99, "BC_EF")
    BC_HI = times(BC, HI, 99 * 99, "BC_HI")
    EF_HI = times(EF, HI, 99 * 99, "EF_HI")
    BC_EF_HI = times(BC_EF, HI, 99 * 99 * 99, "BC_EF_HI")
    A_EF_HI = times(A, EF_HI, 9 * 99 * 99, "A_EF_HI")
    D_BC_HI = times(D, BC_HI, 9 * 99 * 99, "D_BC_HI")
    G_BC_EF = times(G, BC_EF, 9 * 99 * 99, "G_BC_EF")
    model.add(A_EF_HI + D_BC_HI + G_BC_EF == BC_EF_HI)

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

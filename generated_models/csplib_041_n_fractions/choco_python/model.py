# csplib_041_n_fractions: a Choco-solver (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install pychoco numpy`) with:
#   python csplib_041_n_fractions.py

from pychoco.model import Model


def create_model(instance):
    """Find nine different non-zero digits A to I such that A / BC + D / EF + G / HI = 1,
    where BC, EF and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    model = Model()

    # The nine digits A to I, each from 1 to 9, all different.
    digits = [model.intvar(1, 9, name=letter) for letter in "ABCDEFGHI"]
    A, B, C, D, E, F, G, H, I = digits
    model.all_different(digits).post()

    # The two-digit numbers BC, EF and HI.
    BC = model.intvar(11, 99, name="BC")
    EF = model.intvar(11, 99, name="EF")
    HI = model.intvar(11, 99, name="HI")
    model.scalar([B, C], [10, 1], "=", BC).post()
    model.scalar([E, F], [10, 1], "=", EF).post()
    model.scalar([H, I], [10, 1], "=", HI).post()

    def product(x, y, lo, hi, name):
        """A new number equal to x times y, between lo and hi."""
        p = model.intvar(lo, hi, name=name)
        model.times(x, y, p).post()
        return p

    # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI so that no fractions remain.
    # The products are built two factors at a time.
    BC_EF = product(BC, EF, 11 * 11, 99 * 99, "BC_EF")
    BC_HI = product(BC, HI, 11 * 11, 99 * 99, "BC_HI")
    EF_HI = product(EF, HI, 11 * 11, 99 * 99, "EF_HI")
    BC_EF_HI = product(BC_EF, HI, 11 * 11 * 11, 99 * 99 * 99, "BC_EF_HI")
    A_EF_HI = product(A, EF_HI, 11 * 11, 9 * 99 * 99, "A_EF_HI")
    D_BC_HI = product(D, BC_HI, 11 * 11, 9 * 99 * 99, "D_BC_HI")
    G_BC_EF = product(G, BC_EF, 11 * 11, 9 * 99 * 99, "G_BC_EF")
    model.scalar([A_EF_HI, D_BC_HI, G_BC_EF, BC_EF_HI], [1, 1, 1, -1], "=", 0).post()

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}, None


if __name__ == "__main__":
    import numpy as np

    model, outputs, objective = create_model({})
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

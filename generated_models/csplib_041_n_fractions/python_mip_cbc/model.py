# csplib_041_n_fractions: a Python-MIP (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install mip numpy`) with:
#   python csplib_041_n_fractions.py

import mip


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC, EF
    and HI are the two-digit numbers formed by B and C, E and F, and H and I."""
    model = mip.Model(solver_name="CBC")

    # An integer variable with the given bounds.
    def int_var(name, lb, ub):
        return model.add_var(name, lb=lb, ub=ub, var_type=mip.INTEGER)

    # A 0/1 variable.
    def bin_var(name):
        return model.add_var(name, var_type=mip.BINARY)

    # The binary digits of value, as 0/1 variables.
    def bits_of(name, value, n_bits):
        bits = [bin_var(f"{name}_b{k}") for k in range(n_bits)]
        model.add_constr(value - mip.xsum((2**k) * b for k, b in enumerate(bits)) == 0)
        return bits

    # p = v * u, where u is the number made of the bits and v is an integer from 0 to v_ub.
    def times_bits(bits, v, v_ub, name):
        p = int_var(name, 0, v_ub * (2 ** len(bits) - 1))
        terms = []
        for k, b in enumerate(bits):
            # t = v when this bit is 1, and 0 otherwise.
            t = int_var(f"{name}_t{k}", 0, v_ub)
            model.add_constr(t - v_ub * b <= 0)
            model.add_constr(t - v <= 0)
            model.add_constr(t - v + v_ub * (1 - b) >= 0)
            terms.append((2**k) * t)
        model.add_constr(p - mip.xsum(terms) == 0)
        return p

    # Each letter stands for a digit from 1 to 9. onehot[name][v - 1] is 1 when the letter is v.
    digit_names = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]
    digit = {}
    onehot = {}
    for name in digit_names:
        digit[name] = int_var(name, 1, 9)
        onehot[name] = [bin_var(f"p_{name}_{v}") for v in range(1, 10)]
        model.add_constr(mip.xsum(onehot[name]) == 1)
        model.add_constr(digit[name] - mip.xsum(v * p for v, p in zip(range(1, 10), onehot[name])) == 0)

    # The nine letters stand for nine different digits, so each digit from 1 to 9 is used once.
    for v in range(9):
        model.add_constr(mip.xsum(onehot[name][v] for name in digit_names) == 1)

    # BC, EF and HI are the two-digit numbers with tens digits B, E, H and units digits C, F, I.
    BC = int_var("BC", 11, 99)
    EF = int_var("EF", 11, 99)
    HI = int_var("HI", 11, 99)
    model.add_constr(BC - 10 * digit["B"] - digit["C"] == 0)
    model.add_constr(EF - 10 * digit["E"] - digit["F"] == 0)
    model.add_constr(HI - 10 * digit["H"] - digit["I"] == 0)

    # The binary digits of BC, EF, HI, A, D and G, used in the products below.
    BC_bits = bits_of("BC", BC, 7)
    EF_bits = bits_of("EF", EF, 7)
    HI_bits = bits_of("HI", HI, 7)
    A_bits = bits_of("A", digit["A"], 4)
    D_bits = bits_of("D", digit["D"], 4)
    G_bits = bits_of("G", digit["G"], 4)

    # Products of the numbers, needed to clear the fractions.
    EF_HI = times_bits(EF_bits, HI, 99, "EFxHI")
    BC_HI = times_bits(BC_bits, HI, 99, "BCxHI")
    BC_EF = times_bits(BC_bits, EF, 99, "BCxEF")
    BC_EF_HI = times_bits(BC_bits, EF_HI, 99 * 99, "BCxEFxHI")
    A_EF_HI = times_bits(A_bits, EF_HI, 99 * 99, "AxEFxHI")
    D_BC_HI = times_bits(D_bits, BC_HI, 99 * 99, "DxBCxHI")
    G_BC_EF = times_bits(G_bits, BC_EF, 99 * 99, "GxBCxEF")

    # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI:
    # A * EF * HI + D * BC * HI + G * BC * EF = BC * EF * HI.
    model.add_constr(A_EF_HI + D_BC_HI + G_BC_EF - BC_EF_HI == 0)

    # The digits, by letter.
    outputs = {name: digit[name] for name in digit_names}
    return model, outputs


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

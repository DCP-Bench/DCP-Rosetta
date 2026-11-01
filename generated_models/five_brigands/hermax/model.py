from hermax.model import Model


def build(instance):
    m = Model()

    # Create variables for each brigand's doubloons
    # A, B, C >= 1; D >= 1; E >= 1
    A = m.int("A", 1, 200)
    B = m.int("B", 1, 200)
    C = m.int("C", 1, 200)
    D = m.int("D", 1, 200)  # D must be even
    E = m.int("E", 1, 200)  # E must be divisible by 3

    # Constraint 1: Total is 200
    m &= (A + B + C + D + E == 200)

    # Constraint 2: 12*A + 3*B + C + D/2 + E/3 = 200
    # To handle division, introduce auxiliary variables
    d_half = m.int("d_half", 0, 100)
    e_third = m.int("e_third", 0, 66)

    # D = 2 * d_half, E = 3 * e_third
    m &= (D == 2 * d_half)
    m &= (E == 3 * e_third)

    # 12*A + 3*B + C + d_half + e_third = 200
    m &= (12 * A + 3 * B + C + d_half + e_third == 200)

    return m, {"A": A, "B": B, "C": C, "D": D, "E": E}

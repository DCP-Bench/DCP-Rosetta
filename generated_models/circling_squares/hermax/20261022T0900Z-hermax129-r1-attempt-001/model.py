from hermax.model import Model


def build(instance):
    # Circling the Squares: place 10 different numbers in circle.
    # A² + B² = F² + G² (given: A=16, B=2, F=8, G=14, so 260 = 260 ✓)
    # B² + C² = G² + H² => 4 + C² = 196 + H² => C² - H² = 192
    # Similarly: E² - K² = 192

    # C² - H² = 192 = (C-H)(C+H)
    # Factor pairs of 192: (2,96), (4,48), (6,32), (8,24), (12,16)
    # With even sums: (2,96)→C=49,H=47; (4,48)→C=26,H=22; (6,32)→C=19,H=13

    m = Model()

    # Fixed values
    A = m.int("A", 16, 16)
    B = m.int("B", 2, 2)
    F = m.int("F", 8, 8)
    G = m.int("G", 14, 14)

    # Variables: choose one of 3 possible (C,H) pairs
    C = m.int("C", 1, 99)
    H = m.int("H", 1, 99)
    ch_choice = m.int("ch_choice", 0, 2)

    # Case 1: ch_choice = 0 => C=49, H=47
    m &= (ch_choice != 0) | (C == 49)
    m &= (ch_choice != 0) | (H == 47)
    # Case 2: ch_choice = 1 => C=26, H=22
    m &= (ch_choice != 1) | (C == 26)
    m &= (ch_choice != 1) | (H == 22)
    # Case 3: ch_choice = 2 => C=19, H=13
    m &= (ch_choice != 2) | (C == 19)
    m &= (ch_choice != 2) | (H == 13)

    # Similarly for E and K: E² - K² = 192
    E = m.int("E", 1, 99)
    K = m.int("K", 1, 99)
    ek_choice = m.int("ek_choice", 0, 2)

    m &= (ek_choice != 0) | (E == 49)
    m &= (ek_choice != 0) | (K == 47)
    m &= (ek_choice != 1) | (E == 26)
    m &= (ek_choice != 1) | (K == 22)
    m &= (ek_choice != 2) | (E == 19)
    m &= (ek_choice != 2) | (K == 13)

    # Now solve for D and I
    # From constraint C² + D² = H² + I²: D² - I² = H² - C² = 47² - 49² (depends on choice)
    # Let's compute for each (C,H) pair:
    # (49,47): D² - I² = 47² - 49² = 2209 - 2401 = -192 => I² - D² = 192
    # (26,22): D² - I² = 22² - 26² = 484 - 676 = -192 => I² - D² = 192
    # (19,13): D² - I² = 13² - 19² = 169 - 361 = -192 => I² - D² = 192
    # Great! All give I² - D² = 192 (same as C² - H²)

    D = m.int("D", 1, 99)
    I = m.int("I", 1, 99)
    di_choice = m.int("di_choice", 0, 2)

    # I² - D² = 192, so same factorization applies (with roles swapped)
    m &= (di_choice != 0) | (I == 49)
    m &= (di_choice != 0) | (D == 47)
    m &= (di_choice != 1) | (I == 26)
    m &= (di_choice != 1) | (D == 22)
    m &= (di_choice != 2) | (I == 19)
    m &= (di_choice != 2) | (D == 13)

    # From D² + E² = I² + K²:
    # This should be satisfied by the constraint system
    # Let's verify: need to add auxiliary constraint
    D_sq = m.int("D_sq", 1, 2500)
    E_sq = m.int("E_sq", 1, 2500)
    I_sq = m.int("I_sq", 1, 2500)
    K_sq = m.int("K_sq", 1, 2500)

    # Assign squares based on choices
    for val in [13, 19, 22, 26, 47, 49]:
        sq = val * val
        m &= (D != val) | (D_sq == sq)
        m &= (E != val) | (E_sq == sq)
        m &= (I != val) | (I_sq == sq)
        m &= (K != val) | (K_sq == sq)

    # Main constraint: D² + E² = I² + K²
    m &= (D_sq + E_sq == I_sq + K_sq)

    # All different constraint
    m &= (A != B) & (A != C) & (A != D) & (A != E) & (A != F) & (A != G) & (A != H) & (A != I) & (A != K)
    m &= (B != C) & (B != D) & (B != E) & (B != F) & (B != G) & (B != H) & (B != I) & (B != K)
    m &= (C != D) & (C != E) & (C != F) & (C != G) & (C != H) & (C != I) & (C != K)
    m &= (D != E) & (D != F) & (D != G) & (D != H) & (D != I) & (D != K)
    m &= (E != F) & (E != G) & (E != H) & (E != I) & (E != K)
    m &= (F != G) & (F != H) & (F != I) & (F != K)
    m &= (G != H) & (G != I) & (G != K)
    m &= (H != I) & (H != K)
    m &= (I != K)

    return m, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I, "K": K}

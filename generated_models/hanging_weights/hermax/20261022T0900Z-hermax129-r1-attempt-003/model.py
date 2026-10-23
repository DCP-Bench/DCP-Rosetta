from hermax.model import Model


def build(instance):
    mdl = Model()
    names = "abcdefghijklm"
    # Each weight is an integer between 1 and 13. Each weight is tied once to
    # four bits, and the bar equations are written over the bits.
    weight = {}
    bits = {}
    for nm in names:
        w = mdl.int(nm, 0, 13)
        mdl &= (w >= 1)
        b = mdl.bool_vector(f"{nm}_bit", 4)
        expr = sum(2 ** k * b[k] for k in range(4))
        mdl &= (w == expr)
        weight[nm] = w
        bits[nm] = expr

    A, B, C, D = (bits[c] for c in "abcd")
    E, F, G, H = (bits[c] for c in "efgh")
    I, J, K, L, M = (bits[c] for c in "ijklm")

    # Weight of the sub-bar hanging from the H bar: H, I and the E-F bar.
    h_sub = H + I + E + F
    # Weight of the sub-bar hanging from the J-K bar: A-B, G-C-D, J and K.
    jk_sub = J + K + (A + B) + (G + C + D)

    # Bottom right: the bar carrying C and D pivots 5 units from C and 1 from D.
    mdl &= (5 * C == D)
    # The bar above it: G at 3 units, the C-D bar at 2 units.
    mdl &= (3 * G == 2 * (C + D))
    # The bar carrying A and B: A at 4 units, B at 1 unit.
    mdl &= (4 * A == B)
    # The E-F bar: E at 3 units, F at 2 units.
    mdl &= (3 * E == 2 * F)
    # The H bar: H at 3 units; the E-F sub-bar at 2 units, I at 3 units.
    mdl &= (3 * H == 2 * (E + F) + 3 * I)
    # The L-M bar: the H sub-bar at 1 unit; L at 1 unit, M at 4 units.
    mdl &= (h_sub == L + 4 * M)
    # The J-K bar: A-B sub-bar at 3 units, J at 2; K at 1, G-C-D sub-bar at 2.
    mdl &= (3 * (A + B) + 2 * J == K + 2 * (G + C + D))
    # Top bar: the L-M sub-bar at 4 units, the J-K sub-bar at 3 units.
    mdl &= (4 * (h_sub + L + M) == 3 * jk_sub)

    outputs = {nm: weight[nm] for nm in names}
    return mdl, outputs

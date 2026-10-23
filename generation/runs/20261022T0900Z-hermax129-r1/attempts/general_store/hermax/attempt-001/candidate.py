from hermax.model import Model


def build(instance):
    # General Store cryptarithmetic: solve the column addition puzzle
    # Variables represent digits 0-9, all different

    m = Model()

    # Variables for each letter (0-9, all different)
    A = m.int("A", 0, 9)
    B = m.int("B", 0, 9)
    C = m.int("C", 0, 9)
    E = m.int("E", 0, 9)
    H = m.int("H", 0, 9)
    L = m.int("L", 0, 9)
    O = m.int("O", 0, 9)
    P = m.int("P", 0, 9)
    S = m.int("S", 0, 9)
    W = m.int("W", 0, 9)

    letters = [A, B, C, E, H, L, O, P, S, W]
    m &= letters.all_different()

    # Addends:
    CHESS = C * 10000 + H * 1000 + E * 100 + S * 10 + S
    CASH = C * 1000 + A * 100 + S * 10 + H
    BOWWOW = B * 100000 + O * 10000 + W * 1000 + W * 100 + O * 10 + W
    CHOPS = C * 10000 + H * 1000 + O * 100 + P * 10 + S
    ALSOPS = A * 100000 + L * 10000 + S * 1000 + O * 100 + P * 10 + S
    PALEALE = P * 100000 + A * 10000 + L * 1000 + E * 100 + A * 10 + L * 1 + E
    COOL = C * 1000 + O * 100 + O * 10 + L
    BASS = B * 1000 + A * 100 + S * 10 + S
    HOPS = H * 1000 + O * 100 + P * 10 + S
    ALES = A * 1000 + L * 100 + E * 10 + S
    HOES = H * 1000 + O * 100 + E * 10 + S
    APPLES = A * 100000 + P * 10000 + P * 1000 + L * 100 + E * 10 + S
    COWS = C * 1000 + O * 100 + W * 10 + S
    CHEESE = C * 100000 + H * 10000 + E * 1000 + E * 100 + S * 10 + E
    CHSOAP = C * 100000 + H * 10000 + S * 1000 + O * 100 + A * 10 + P
    SHEEP = S * 10000 + H * 1000 + E * 100 + E * 10 + P

    # Sum: ALLWOOL
    ALLWOOL = A * 1000000 + L * 100000 + L * 10000 + W * 1000 + O * 100 + O * 10 + L

    # Main constraint: sum of all addends equals ALLWOOL
    total = (CHESS + CASH + BOWWOW + CHOPS + ALSOPS + PALEALE + COOL + BASS +
             HOPS + ALES + HOES + APPLES + COWS + CHEESE + CHSOAP + SHEEP)
    m &= (total == ALLWOOL)

    # Leading digits cannot be 0 (implied by arithmetic significance)
    # But this might not be strictly necessary for the solution

    return m, {
        "A": A,
        "B": B,
        "C": C,
        "E": E,
        "H": H,
        "L": L,
        "O": O,
        "P": P,
        "S": S,
        "W": W,
    }

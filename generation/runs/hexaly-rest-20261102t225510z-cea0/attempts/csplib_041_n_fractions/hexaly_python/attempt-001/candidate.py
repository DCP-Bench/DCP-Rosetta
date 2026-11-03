"""N fractions: distinct non-zero digits A..I with A / BC + D / EF + G / HI = 1."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The nine digits are different and non-zero
    digits = [model.int(1, 9) for _ in range(9)]
    for a in range(9):
        for b in range(a + 1, 9):
            model.constraint(digits[a] != digits[b])
    A, B, C, D, E, F, G, H, I = digits

    # BC, EF and HI are the two-digit numbers they spell
    bc, ef, hi = 10 * B + C, 10 * E + F, 10 * H + I
    # A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI to stay in integers
    model.constraint(A * ef * hi + D * bc * hi + G * bc * ef == bc * ef * hi)

    return optimizer, {"A": A, "B": B, "C": C, "D": D, "E": E, "F": F, "G": G, "H": H, "I": I}

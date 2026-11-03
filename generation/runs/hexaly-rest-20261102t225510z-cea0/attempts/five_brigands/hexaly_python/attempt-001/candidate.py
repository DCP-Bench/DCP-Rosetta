"""Five brigands: the doubloons of each of five brigands, 200 in all, still 200 if scaled by 12, 3, 1, 1/2 and 1/3."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # Each brigand has at least one doubloon; Diego's half and Esteban's third are whole numbers
    A, B, C = (model.int(1, 200) for _ in range(3))
    half_d, third_e = model.int(1, 100), model.int(1, 66)
    D, E = 2 * half_d, 3 * third_e

    # They have 200 doubloons altogether
    model.constraint(A + B + C + D + E == 200)
    # With twelve times, three times, the same, half and a third they still have 200
    model.constraint(12 * A + 3 * B + C + half_d + third_e == 200)

    return optimizer, {"A": A, "B": B, "C": C, "D": D, "E": E}

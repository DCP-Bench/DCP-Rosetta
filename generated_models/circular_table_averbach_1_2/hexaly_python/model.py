"""Circular table: three players X, Y, Z of different nationalities sit round a table; each passed three cards to
the person on their right. Seats 0, 1, 2 run to the right: seat 1 is right of seat 0, seat 0 right of seat 2."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # The seat (0, 1 or 2) of each player, and of the person with each nationality; the same seat
    # means the same person
    x, y, z = (model.int(0, 2) for _ in range(3))
    american, english, french = (model.int(0, 2) for _ in range(3))  # the seat of the person with each nationality
    for group in ([x, y, z], [american, english, french]):
        for a in range(3):
            for b in range(a + 1, 3):
                model.constraint(group[a] != group[b])

    def right_of(seat):
        return (seat + 1) % 3

    # Y passed three hearts to the American, who sits on Y's right
    model.constraint(american == right_of(y))
    # X passed the queen of spades and two diamonds to the person who passed cards to the Frenchwoman:
    # that person has the Frenchwoman on their right, so they sit on the right of X
    model.constraint(right_of(right_of(x)) == french)

    return optimizer, {"x": x, "y": y, "z": z, "american": american, "english": english, "french": french}

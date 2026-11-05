"""Five floors: Baker, Cooper, Fletcher, Miller and Smith live on different floors of the first five."""
import hexaly.optimizer as hx


def build(instance):
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    B, C, F, M, S = (model.int(1, 5) for _ in range(5))  # the floor (1 to 5) of Baker, Cooper, Fletcher, Miller and Smith
    # They all live on different floors
    people = [B, C, F, M, S]
    for a in range(5):
        for b in range(a + 1, 5):
            model.constraint(people[a] != people[b])

    model.constraint(B != 5)              # Baker does not live on the fifth floor
    model.constraint(C != 1)              # Cooper does not live on the first floor
    model.constraint(F != 5)              # Fletcher lives on neither the fifth
    model.constraint(F != 1)              # nor the first floor
    model.constraint(M > C)               # Miller lives higher than Cooper
    model.constraint(model.abs(S - F) != 1)  # Smith is not next to Fletcher
    model.constraint(model.abs(F - C) != 1)  # Fletcher is not next to Cooper

    return optimizer, {"B": B, "C": C, "F": F, "M": M, "S": S}

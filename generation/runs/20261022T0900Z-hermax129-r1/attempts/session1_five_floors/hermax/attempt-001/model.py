from hermax.model import Model


def build(instance):
    # Five people on five distinct floors numbered 1 to 5.
    m = Model()
    floors = m.int_vector("floor", 5, 1, 5)
    B, C, F, M, S = floors[0], floors[1], floors[2], floors[3], floors[4]

    # They all live on different floors.
    m &= floors.all_different()

    # Baker does not live on the fifth floor.
    m &= (B != 5)

    # Cooper does not live on the first floor.
    m &= (C != 1)

    # Fletcher does not live on either the fifth or the first floor.
    m &= (F != 5)
    m &= (F != 1)

    # Miller lives on a higher floor than Cooper.
    m &= (M >= C + 1)

    # Smith does not live on a floor adjacent to Fletcher's.
    # Fletcher does not live on a floor adjacent to Cooper's.
    # Each is a half-reified rule: for every floor f, the neighbour floors
    # f - 1 and f + 1 are excluded when the other person is on f.
    for f in range(1, 6):
        m &= (S != f + 1).only_if(F == f)
        m &= (S != f - 1).only_if(F == f)
        m &= (F != f + 1).only_if(C == f)
        m &= (F != f - 1).only_if(C == f)

    return m, {"B": B, "C": C, "F": F, "M": M, "S": S}

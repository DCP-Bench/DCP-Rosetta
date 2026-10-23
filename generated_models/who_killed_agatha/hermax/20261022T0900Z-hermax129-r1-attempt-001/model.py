from hermax.model import Model


# The three people of the puzzle, by index: Agatha, the butler, Charles.
AGATHA, BUTLER, CHARLES = 0, 1, 2


def build(instance):
    people = range(len(instance["names"]))

    m = Model()
    # hates[i][j] is true when person i hates person j.
    hates = m.bool_matrix("hates", 3, 3)
    # wealth[i] is the wealth of person i on a small scale.
    wealth = m.int_vector("wealth", 3, 0, 10)
    # killer is the index of the person who killed Agatha.
    killer = m.int("killer", 0, 2)

    # Agatha hates everybody except the butler.
    for j in people:
        if j == BUTLER:
            m &= ~hates[AGATHA][j]
        else:
            m &= hates[AGATHA][j]

    # Charles hates no one that Agatha hates.
    for j in people:
        m &= (~hates[AGATHA][j]) | (~hates[CHARLES][j])

    # The butler hates everyone whom Agatha hates.
    for j in people:
        m &= (~hates[AGATHA][j]) | hates[BUTLER][j]

    # The butler hates everyone not richer than Aunt Agatha.
    for j in people:
        not_richer = m.bool()
        m &= (wealth[j] - wealth[AGATHA] <= 0).iff(not_richer)
        m &= (~not_richer) | hates[BUTLER][j]

    # Noone hates everyone.
    for i in people:
        m &= (~hates[i][0]) | (~hates[i][1]) | (~hates[i][2])

    # A killer always hates his victim (Agatha), and is no richer than her.
    for i in people:
        is_killer = (killer == i)
        m &= (~is_killer) | hates[i][AGATHA]
        not_richer_than_victim = m.bool()
        m &= (wealth[i] - wealth[AGATHA] <= 0).iff(not_richer_than_victim)
        m &= (~is_killer) | not_richer_than_victim

    return m, {"killer": killer}

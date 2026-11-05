"""Who killed Agatha: the three residents of Dreadsbury Mansion, and who hates and who is richer than whom."""
import hexaly.optimizer as hx

AGATHA, BUTLER, CHARLES = 0, 1, 2  # the order of the residents in the data


def build(instance):
    n = len(instance["names"])  # the number of residents of the mansion
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # killer is one of the residents; the victim is Aunt Agatha
    killer = model.int(0, n - 1)
    # hates[x][y] = 1 if x hates y; richer[x][y] = 1 if x is richer than y
    hates = [[model.bool() for _ in range(n)] for _ in range(n)]
    richer = [[model.bool() for _ in range(n)] for _ in range(n)]

    # Richer is a strict relation: nobody is richer than themselves, and two people are not each richer than the other
    for x in range(n):
        model.constraint(richer[x][x] == 0)
        for y in range(x + 1, n):
            model.constraint(richer[x][y] + richer[y][x] <= 1)

    # A killer hates the victim and is no richer than the victim
    killer_hates = model.at(model.array([hates[x][AGATHA] for x in range(n)]), killer)
    killer_richer = model.at(model.array([richer[x][AGATHA] for x in range(n)]), killer)
    model.constraint(killer_hates == 1)
    model.constraint(killer_richer == 0)  # the killer is no richer than the victim

    for y in range(n):
        # Charles hates no one that Agatha hates
        model.constraint(hates[AGATHA][y] + hates[CHARLES][y] <= 1)
        # Agatha hates everybody except the butler
        model.constraint(hates[AGATHA][y] == (0 if y == BUTLER else 1))
        # The butler hates everyone not richer than Agatha
        model.constraint(model.or_(richer[y][AGATHA] == 1, hates[BUTLER][y] == 1))
        # The butler hates everyone whom Agatha hates
        model.constraint(hates[AGATHA][y] <= hates[BUTLER][y])
    # No one hates everyone
    for x in range(n):
        model.constraint(model.sum(hates[x]) <= n - 1)

    return optimizer, {"killer": killer}

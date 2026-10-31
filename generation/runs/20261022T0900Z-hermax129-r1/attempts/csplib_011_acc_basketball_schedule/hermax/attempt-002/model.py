from itertools import permutations

from hermax.model import Model

# Fixed constants of the problem: team indices in the order the description lists them.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
# Rival pairs (every team except FSU has one).
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
# Mirroring scheme from the description, dates 1-based.
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def build(instance):
    n = instance["n_teams"]
    D = instance["n_days"]
    # Day index d is date d + 1. Odd dates (index even) are weekdays, even dates (index odd) weekends.
    weekends = [d for d in range(D) if d % 2 == 1]

    m = Model()

    # H[d][i][j]: team i hosts team j on day d.
    H = [[[None] * n for _ in range(n)] for _ in range(D)]
    for d in range(D):
        for i in range(n):
            for j in range(n):
                if i != j:
                    H[d][i][j] = m.bool()

    # PP[d][(i, j)] with i < j: teams i and j play each other on day d, at either venue.
    PP = [dict() for _ in range(D)]
    for d in range(D):
        for i in range(n):
            for j in range(i + 1, n):
                p = m.bool()
                m &= (~p | H[d][i][j] | H[d][j][i])
                m &= (p | ~H[d][i][j])
                m &= (p | ~H[d][j][i])
                PP[d][(i, j)] = p

    def plays(d, i, j):
        return PP[d][(min(i, j), max(i, j))]

    # Per team and day: exactly one of home, away, bye.
    hm = [[m.bool() for _ in range(n)] for _ in range(D)]
    am = [[m.bool() for _ in range(n)] for _ in range(D)]
    bye = [[m.bool() for _ in range(n)] for _ in range(D)]
    for d in range(D):
        for i in range(n):
            home = [H[d][i][j] for j in range(n) if j != i]
            away = [H[d][j][i] for j in range(n) if j != i]
            m &= (sum(home) <= 1)
            m &= (sum(away) <= 1)
            m &= (sum(home) == 1).iff(hm[d][i])
            m &= (sum(away) == 1).iff(am[d][i])
            m &= (hm[d][i] + am[d][i] + bye[d][i] == 1)

    # Double round robin: each ordered pair meets exactly once at home.
    for i in range(n):
        for j in range(n):
            if i != j:
                m &= (sum(H[d][i][j] for d in range(D)) == 1)

    # Weekend pattern: four home, four away, one bye on the weekends.
    for i in range(n):
        m &= (sum(hm[d][i] for d in weekends) == 4)
        m &= (sum(am[d][i] for d in weekends) == 4)
        m &= (sum(bye[d][i] for d in weekends) == 1)

    # Mirroring: the same opponent on both dates of each pair.
    for r1, r2 in MIRROR:
        for i in range(n):
            for j in range(i + 1, n):
                a = plays(r1 - 1, i, j)
                b = plays(r2 - 1, i, j)
                m &= (~a | b)
                m &= (a | ~b)

    for i in range(n):
        # No two final aways (last two dates).
        m &= (~am[D - 2][i] | ~am[D - 1][i])

        # Home/away/bye patterns in a row.
        for d in range(D - 2):
            m &= (~am[d][i] | ~am[d + 1][i] | ~am[d + 2][i])  # at most two away in a row
            m &= (~hm[d][i] | ~hm[d + 1][i] | ~hm[d + 2][i])  # at most two home in a row
        for d in range(D - 3):
            # at most three away-or-bye in a row: a home match in every four dates
            m &= (hm[d][i] | hm[d + 1][i] | hm[d + 2][i] | hm[d + 3][i])
        for d in range(D - 4):
            # at most four home-or-bye in a row: an away match in every five dates
            m &= (am[d][i] | am[d + 1][i] | am[d + 2][i] | am[d + 3][i] | am[d + 4][i])

        # Each team has home matches or byes on at least two of the first five weekends.
        first_weekends = weekends[:5]
        m &= (sum(hm[d][i] for d in first_weekends) + sum(bye[d][i] for d in first_weekends) >= 2)

    # Rival matches on the last date, unless the team plays FSU or has a bye.
    for i, r in RIVAL.items():
        m &= (plays(D - 1, i, r) | plays(D - 1, i, FSU) | bye[D - 1][i])

    # Constrained matches within dates 11 to 18 (indices 10 to 17).
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        m &= (sum(plays(d, a, b) for d in range(10, D)) >= 1)

    # Opponent sequences: no consecutive away games at UNC and Duke.
    for i in range(n):
        if i in (UNC, DUKE):
            continue
        for d in range(D - 1):
            m &= (~H[d][UNC][i] | ~H[d + 1][DUKE][i])
            m &= (~H[d][DUKE][i] | ~H[d + 1][UNC][i])

    # No three consecutive dates against UNC, Duke and Wake, in any order.
    for i in range(n):
        if i in (UNC, DUKE, WAKE):
            continue
        for d in range(D - 2):
            for a, b, c in permutations([UNC, DUKE, WAKE]):
                m &= (~plays(d, i, a) | ~plays(d + 1, i, b) | ~plays(d + 2, i, c))

    # Other constraints (dates converted to indices).
    m &= plays(1, UNC, CLEM)            # UNC plays Clem on date 2
    m &= plays(D - 1, UNC, DUKE)        # UNC plays Duke on the last date
    m &= plays(10, UNC, DUKE)           # UNC plays Duke on date 11
    m &= bye[15][DUKE]                  # Duke has a bye on date 16
    m &= ~hm[16][WAKE]                  # Wake does not play home on date 17
    m &= bye[0][WAKE]                   # Wake has a bye on date 1
    for i in (CLEM, DUKE, UMD, WAKE):
        m &= ~am[D - 1][i]              # no away match on the last date
    for i in (CLEM, FSU, GT, WAKE):
        m &= ~am[0][i]                  # no away match on the first date
    m &= ~bye[D - 1][FSU]
    m &= ~bye[D - 1][NCST]
    m &= ~bye[0][UNC]

    # Outputs: config[d][i] is the opponent of team i on day d (own index on a bye),
    # where[d][i] is 0 at home, 2 away, 1 bye.
    config = m.int_matrix("config", D, n, 0, n - 1)
    where = m.int_matrix("where", D, n, 0, 2)
    for d in range(D):
        for i in range(n):
            terms = [j * H[d][i][j] for j in range(1, n) if j != i]
            terms += [j * H[d][j][i] for j in range(1, n) if j != i]
            if i > 0:
                terms.append(i * bye[d][i])
            m &= (config[d][i] == sum(terms))
            m &= (where[d][i] == 2 * am[d][i] + bye[d][i])

    return m, {"config": config, "where": where}

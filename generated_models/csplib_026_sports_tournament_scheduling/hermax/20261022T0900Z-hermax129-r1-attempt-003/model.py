from hermax.model import Model


def build(instance):
    n = instance["n_teams"]     # teams numbered 1..n in the output
    W = n - 1                   # weeks
    P = n // 2                  # periods per week, two slots each

    m = Model()
    home = m.int_matrix("home", W, P, 1, n)
    away = m.int_matrix("away", W, P, 1, n)

    # Every team plays once a week: the 2P slots of a week hold each team exactly once.
    for w in range(W):
        slots = m.int_vector(f"slot{w}", n, 1, n)
        m &= slots.all_different()
        for p in range(P):
            m &= (home[w][p] == slots[2 * p])
            m &= (away[w][p] == slots[2 * p + 1])

    # Every team plays at most twice in the same period over the tournament.
    for t in range(1, n + 1):
        for p in range(P):
            m &= (sum([(home[w][p] == t) for w in range(W)]
                      + [(away[w][p] == t) for w in range(W)]) <= 2)

    # Every team plays every other team exactly once (one home and one away game between them).
    # z[w][p][i][j] is true when team i hosts team j in week w, period p.
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            meetings = []
            for w in range(W):
                for p in range(P):
                    for x, y in ((i, j), (j, i)):
                        z = m.bool()
                        hx = (home[w][p] == x)
                        ay = (away[w][p] == y)
                        m &= (~z | hx)
                        m &= (~z | ay)
                        m &= (z | ~hx | ~ay)
                        meetings.append(z)
            m &= (sum(meetings) == 1)

    return m, {"home": home, "away": away}

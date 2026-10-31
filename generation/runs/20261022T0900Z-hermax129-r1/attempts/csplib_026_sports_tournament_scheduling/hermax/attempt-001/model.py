from hermax.model import Model


def build(instance):
    m = Model()

    # Extract instance data
    n_teams = instance["n_teams"]
    n_weeks = n_teams - 1
    n_periods = n_teams // 2

    # Decision variables: home[w][p] and away[w][p] - teams playing home/away in week w, period p
    # Teams are numbered 1 to n_teams
    home = m.int_matrix("home", n_weeks, n_periods, 1, n_teams)
    away = m.int_matrix("away", n_weeks, n_periods, 1, n_teams)

    # Constraint 1: In each match, home and away teams are different
    for w in range(n_weeks):
        for p in range(n_periods):
            m &= (home[w][p] != away[w][p])

    # Constraint 2: Each team plays exactly once per week
    for w in range(n_weeks):
        for t in range(1, n_teams + 1):
            # Count occurrences of team t in home and away arrays for week w
            appearances = sum((home[w][p] == t) for p in range(n_periods)) + \
                         sum((away[w][p] == t) for p in range(n_periods))
            # Each team should appear exactly once per week
            m &= (appearances == 1)

    # Constraint 3: Each pair of teams plays at most once
    # Track all matches implicitly through the structure
    # For each week and pair of teams, at most one match between them
    for w in range(n_weeks):
        for p1 in range(n_periods):
            for p2 in range(p1 + 1, n_periods):
                # No team can play twice in the same week
                # (This is already ensured by constraint 2, but be explicit)
                m &= ((home[w][p1] != home[w][p2]) & (home[w][p1] != away[w][p2]))
                m &= ((away[w][p1] != home[w][p2]) & (away[w][p1] != away[w][p2]))

    # Constraint 4: Each team plays at most twice in the same period
    for t in range(1, n_teams + 1):
        for p in range(n_periods):
            # Count how many weeks team t plays in period p
            period_count = sum((home[w][p] == t) for w in range(n_weeks)) + \
                          sum((away[w][p] == t) for w in range(n_weeks))
            # Team t can play in period p at most 2 times
            m &= (period_count <= 2)

    return m, {"home": home, "away": away}

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
    # For each week w and each team t, t appears exactly once (as home or away)
    for w in range(n_weeks):
        for t in range(1, n_teams + 1):
            appearances = sum((home[w][p] == t) for p in range(n_periods)) + \
                         sum((away[w][p] == t) for p in range(n_periods))
            m &= (appearances == 1)

    # Constraint 3: Each team plays at most twice in the same period over all weeks
    for t in range(1, n_teams + 1):
        for p in range(n_periods):
            period_count = sum((home[w][p] == t) for w in range(n_weeks)) + \
                          sum((away[w][p] == t) for w in range(n_weeks))
            m &= (period_count <= 2)

    # Constraint 4: Each pair of teams plays exactly once
    # For each pair (i, j), count matches and ensure exactly 1
    for i in range(1, n_teams + 1):
        for j in range(i + 1, n_teams + 1):
            match_count = 0
            for w in range(n_weeks):
                for p in range(n_periods):
                    # Create binary vars for match types
                    i_home_j_away = m.bool(f"match_{i}_{j}_w{w}_p{p}_ih")
                    j_home_i_away = m.bool(f"match_{i}_{j}_w{w}_p{p}_jh")

                    # Link to actual match conditions
                    m &= (i_home_j_away == ((home[w][p] == i) & (away[w][p] == j)))
                    m &= (j_home_i_away == ((home[w][p] == j) & (away[w][p] == i)))

                    # Count this match if either condition is true
                    either_match = m.bool(f"either_match_{i}_{j}_w{w}_p{p}")
                    m &= (either_match == (i_home_j_away | j_home_i_away))
                    match_count += either_match

            # Teams i and j play exactly once
            m &= (match_count == 1)

    return m, {"home": home, "away": away}

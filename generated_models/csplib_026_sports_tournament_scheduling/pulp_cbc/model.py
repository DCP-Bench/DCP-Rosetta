# csplib_026_sports_tournament_scheduling: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

import pulp


def create_model(instance):
    """Schedule a round-robin tournament of n teams over n - 1 weeks. Each week has n / 2 periods,
    and each period holds one match, with a home team and an away team. Every team plays once a
    week, every pair of teams meets, and no team plays more than twice in the same period."""
    n = instance["n_teams"]  # the number of teams
    n_weeks, n_periods = n - 1, n // 2  # the tournament length, and the periods in each week
    teams = range(1, n + 1)  # the teams, numbered 1 to n
    weeks = range(n_weeks)  # the weeks of the tournament
    periods = range(n_periods)  # the periods of each week
    matches = [(i, j) for i in teams for j in teams if i != j]  # the (home, away) pairs of different teams

    problem = pulp.LpProblem("sports_tournament_scheduling", pulp.LpMinimize)

    # play[w][p][(i, j)] is 1 when team i plays at home against team j in week w, period p, and 0 when not.
    play = [[{(i, j): pulp.LpVariable(f"play_{w}_{p}_{i}_{j}", cat="Binary") for i, j in matches}
             for p in periods] for w in weeks]

    # The matches that team t plays in week w, period p, at home or away.
    def involves(w, p, t):
        return pulp.lpSum(var for (i, j), var in play[w][p].items() if t in (i, j))

    # Each period of each week holds exactly one match.
    for w in weeks:
        for p in periods:
            problem += pulp.lpSum(play[w][p].values()) == 1

    # Each team plays once a week.
    for w in weeks:
        for t in teams:
            problem += pulp.lpSum(involves(w, p, t) for p in periods) == 1

    # Each pair of teams meets at least once, in either order.
    for i in teams:
        for j in teams:
            if i < j:
                problem += pulp.lpSum(play[w][p][(i, j)] + play[w][p][(j, i)]
                                      for w in weeks for p in periods) >= 1

    # No team plays more than twice in the same period over the tournament.
    for t in teams:
        for p in periods:
            problem += pulp.lpSum(involves(w, p, t) for w in weeks) <= 2

    # The team at home, and the team away, in each week and period.
    home = [[pulp.lpSum(i * var for (i, j), var in play[w][p].items()) for p in periods]
            for w in weeks]
    away = [[pulp.lpSum(j * var for (i, j), var in play[w][p].items()) for p in periods]
            for w in weeks]
    return problem, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

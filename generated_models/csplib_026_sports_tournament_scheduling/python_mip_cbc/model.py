# csplib_026_sports_tournament_scheduling: a Python-MIP (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install mip numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

import mip


def create_model(instance):
    """Schedule a round-robin tournament of n teams over n - 1 weeks. Each week has n / 2 periods,
    and each period holds one match, in which the first team plays at home and the second team
    plays away. Every team plays once a week, at most twice in the same period over the
    tournament, and every team plays every other team."""
    n_teams = instance["n_teams"]  # the number of teams n, which is even, numbered 1 to n
    n_weeks = n_teams - 1         # one week for each of the other teams
    n_periods = n_teams // 2      # the periods of a week, one match in each
    teams = range(n_teams)        # the teams, numbered 0 to n - 1 here

    model = mip.Model(solver_name="CBC")

    # match[w, p, i, j] is 1 when team i plays at home against team j in week w, period p
    match = {}
    for w in range(n_weeks):
        for p in range(n_periods):
            for i in teams:
                for j in teams:
                    if i != j:
                        match[w, p, i, j] = model.add_var(f"match_{w}_{p}_{i}_{j}", var_type=mip.BINARY)

    # The expression is 1 when team t plays at home in week w, period p.
    def at_home(w, p, t):
        return mip.xsum(match[w, p, t, j] for j in teams if j != t)

    # The expression is 1 when team t plays away in week w, period p.
    def at_away(w, p, t):
        return mip.xsum(match[w, p, i, t] for i in teams if i != t)

    # Each period of each week holds exactly one match.
    for w in range(n_weeks):
        for p in range(n_periods):
            model += mip.xsum(match[w, p, i, j] for i in teams for j in teams if i != j) == 1

    # Every team plays once a week.
    for w in range(n_weeks):
        for t in teams:
            model += mip.xsum(at_home(w, p, t) + at_away(w, p, t) for p in range(n_periods)) == 1

    # Every team plays at most twice in the same period over the tournament.
    for p in range(n_periods):
        for t in teams:
            model += mip.xsum(at_home(w, p, t) + at_away(w, p, t) for w in range(n_weeks)) <= 2

    # Every two teams play each other exactly once.
    for i in teams:
        for j in teams:
            if i < j:
                model += (
                    mip.xsum(match[w, p, i, j] + match[w, p, j, i] for w in range(n_weeks) for p in range(n_periods))
                    == 1
                )

    # home[w][p] and away[w][p] are the team numbers (1 to n_teams) at home and away in week w, period p.
    home = [[None] * n_periods for _ in range(n_weeks)]
    away = [[None] * n_periods for _ in range(n_weeks)]
    for w in range(n_weeks):
        for p in range(n_periods):
            home[w][p] = model.add_var(f"home_{w}_{p}", lb=1, ub=n_teams, var_type=mip.INTEGER)
            away[w][p] = model.add_var(f"away_{w}_{p}", lb=1, ub=n_teams, var_type=mip.INTEGER)
            model += home[w][p] == mip.xsum((t + 1) * at_home(w, p, t) for t in teams)
            model += away[w][p] == mip.xsum((t + 1) * at_away(w, p, t) for t in teams)

    # There is no objective: any tournament that meets the rules is an answer.
    return model, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.verbose = 0  # no solver log
    model.max_mip_gap = 0  # prove the optimum; the default stops within 0.01% of it
    status = model.optimize()

    if status == mip.OptimizationStatus.OPTIMAL:
        value = np.vectorize(lambda var: round(var.x))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", status.name)

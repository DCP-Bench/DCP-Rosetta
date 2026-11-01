# csplib_026_sports_tournament_scheduling: a CPMpy model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install cpmpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

import numpy as np
import cpmpy as cp


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks, each week with n / 2 periods, each period
    holding one match (a home team and an away team). Every team plays once a week, at most twice
    in the same period over the tournament, and every team plays every other team."""
    n_teams = instance["n_teams"]  # the number of teams n (even), numbered from 1
    n_weeks = n_teams - 1          # every team meets the n - 1 others, one per week
    n_periods = n_teams // 2       # matches per week: two teams per match, every team plays

    # home[w, p] is the home team of the match in week w, period p
    home = cp.intvar(1, n_teams, shape=(n_weeks, n_periods), name="home")
    # away[w, p] is the away team of the match in week w, period p
    away = cp.intvar(1, n_teams, shape=(n_weeks, n_periods), name="away")

    model = cp.Model()

    # A team does not play against itself.
    model.add(home != away)

    # Every team plays exactly once a week: the n_teams places of a week (home and away of each
    # period) hold n_teams different teams.
    for w in range(n_weeks):
        model.add(cp.AllDifferent(np.append(home[w], away[w])))

    # Every team meets every other team, as home or away, in at least one match.
    for t1 in range(1, n_teams + 1):
        for t2 in range(t1 + 1, n_teams + 1):
            model.add((cp.sum((home == t1) & (away == t2)) + cp.sum((home == t2) & (away == t1))) >= 1)

    # Every team plays at most twice in the same period over the tournament.
    for t in range(1, n_teams + 1):
        for p in range(n_periods):
            model.add(cp.sum((home[:, p] == t) | (away[:, p] == t)) <= 2)

    return model, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    if model.solve():
        for name, variables in outputs.items():
            print(name, "=", variables.value())
    else:
        print("No solution:", model.status())

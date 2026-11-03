# csplib_026_sports_tournament_scheduling: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from exact import Exact


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks. Each week has n / 2 periods, and each
    period is one match with a home team and an away team. Every team plays once a week, at most
    twice in the same period over the tournament, and meets every other team."""
    n_teams = instance["n_teams"]   # the number of teams n, numbered 1 to n; n is even
    n_weeks = n_teams - 1           # every team meets each of the other n - 1 teams once
    n_periods = n_teams // 2        # the matches in a week, one per period
    teams = range(1, n_teams + 1)   # the team numbers

    solver = Exact()

    # Exact identifies its variables by name.
    # home[w][p] is the team at home in the match of week w, period p; away[w][p] is the team away
    home = [[f"home_{w}_{p}" for p in range(n_periods)] for w in range(n_weeks)]
    away = [[f"away_{w}_{p}" for p in range(n_periods)] for w in range(n_weeks)]
    # at_home[w, p, t] is 1 when team t is the home team of the match in week w, period p, and 0
    # when not; at_away[w, p, t] is the same for the away team
    at_home = {}
    at_away = {}
    for w in range(n_weeks):
        for p in range(n_periods):
            solver.addVariable(home[w][p], 1, n_teams)
            solver.addVariable(away[w][p], 1, n_teams)
            for t in teams:
                at_home[w, p, t] = f"at_home_{w}_{p}_{t}"
                at_away[w, p, t] = f"at_away_{w}_{p}_{t}"
                solver.addVariable(at_home[w, p, t], 0, 1)
                solver.addVariable(at_away[w, p, t], 0, 1)
            # Each match has exactly one home team and exactly one away team.
            solver.addConstraint([(1, at_home[w, p, t]) for t in teams], True, 1, True, 1)
            solver.addConstraint([(1, at_away[w, p, t]) for t in teams], True, 1, True, 1)
            # The home and away teams are the teams marked above.
            solver.addConstraint([(t, at_home[w, p, t]) for t in teams] + [(-1, home[w][p])],
                                 True, 0, True, 0)
            solver.addConstraint([(t, at_away[w, p, t]) for t in teams] + [(-1, away[w][p])],
                                 True, 0, True, 0)
            # A team cannot play itself: it is not both home and away in the same match.
            for t in teams:
                solver.addConstraint([(1, at_home[w, p, t]), (1, at_away[w, p, t])],
                                     False, 0, True, 1)

    # Every team plays once a week: it is home or away in exactly one match of the week.
    for w in range(n_weeks):
        for t in teams:
            solver.addConstraint([(1, at_home[w, p, t]) for p in range(n_periods)]
                                 + [(1, at_away[w, p, t]) for p in range(n_periods)],
                                 True, 1, True, 1)

    # Every team plays at most twice in the same period over the tournament.
    for t in teams:
        for p in range(n_periods):
            solver.addConstraint([(1, at_home[w, p, t]) for w in range(n_weeks)]
                                 + [(1, at_away[w, p, t]) for w in range(n_weeks)],
                                 False, 0, True, 2)

    # Every team meets every other team at least once.
    for t1 in teams:
        for t2 in teams:
            if t1 >= t2:
                continue
            # meets[w][p] is 1 when teams t1 and t2 both play in the match of week w, period p
            meets = []
            for w in range(n_weeks):
                for p in range(n_periods):
                    name = f"meets_{w}_{p}_{t1}_{t2}"
                    solver.addVariable(name, 0, 1)
                    # A meeting in a match needs both teams to play in it.
                    solver.addConstraint([(1, name), (-1, at_home[w, p, t1]), (-1, at_away[w, p, t1])],
                                         False, 0, True, 0)
                    solver.addConstraint([(1, name), (-1, at_home[w, p, t2]), (-1, at_away[w, p, t2])],
                                         False, 0, True, 0)
                    meets.append((1, name))
            solver.addConstraint(meets, True, 1)

    return solver, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

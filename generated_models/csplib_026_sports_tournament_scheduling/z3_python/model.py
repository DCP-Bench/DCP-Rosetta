# csplib_026_sports_tournament_scheduling: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

import z3


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks. Each week has n / 2 periods, and each
    period holds one match between a home team and an away team. Every team plays once a week,
    at most twice in the same period over the tournament, and plays every other team."""
    n_teams = instance["n_teams"]  # the number of teams, numbered from 1
    n_weeks = n_teams - 1          # the number of weeks in the tournament
    n_periods = n_teams // 2       # the number of matches in each week
    teams = range(1, n_teams + 1)  # the team numbers

    # home[w][p] is the team playing at home in week w, period p
    home = [[z3.Int(f"home_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]
    # away[w][p] is the team playing away in the same match
    away = [[z3.Int(f"away_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]

    solver = z3.Solver()

    # Each place holds a team from 1 to n_teams.
    solver.add([z3.And(t >= 1, t <= n_teams) for row in home + away for t in row])

    # No team plays against itself.
    solver.add([home[w][p] != away[w][p] for w in range(n_weeks) for p in range(n_periods)])

    # Every team plays exactly once a week, so the places of each week hold different teams.
    solver.add([z3.Distinct(home[w] + away[w]) for w in range(n_weeks)])

    # Every two teams play each other in at least one match, at home or away.
    for t1 in teams:
        for t2 in range(t1 + 1, n_teams + 1):
            solver.add(z3.Or([z3.Or(z3.And(home[w][p] == t1, away[w][p] == t2),
                                    z3.And(home[w][p] == t2, away[w][p] == t1))
                              for w in range(n_weeks) for p in range(n_periods)]))

    # A team plays at most twice in the same period over the tournament.
    for t in teams:
        for p in range(n_periods):
            solver.add(z3.AtMost(*[z3.Or(home[w][p] == t, away[w][p] == t)
                                   for w in range(n_weeks)], 2))

    return solver, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])

    status = solver.check()
    if status == z3.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output, model_completion=True))
    else:
        print("No solution:", status)

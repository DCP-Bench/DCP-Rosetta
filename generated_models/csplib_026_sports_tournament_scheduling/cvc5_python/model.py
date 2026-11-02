# csplib_026_sports_tournament_scheduling: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

import itertools

import cvc5.pythonic as c5


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks. Each week has n / 2 periods, and each
    period holds one match between a home team and an away team. Every team plays once a week,
    every team plays at most twice in the same period over the tournament, and every team plays
    every other team."""
    n_teams = instance["n_teams"]  # n, the number of teams, numbered 1 to n
    n_weeks = n_teams - 1          # one week for each of the other teams a team plays
    n_periods = n_teams // 2       # the periods of a week, one match in each
    teams = range(1, n_teams + 1)

    # play[w, p, i, j] is true when in week w, period p, team i plays at home against team j.
    play = {(w, p, i, j): c5.Bool(f"play_{w}_{p}_{i}_{j}")
            for w in range(n_weeks) for p in range(n_periods)
            for i in teams for j in teams if i != j}

    # inslot[w, p, t] is true when team t takes part in the match of week w, period p.
    inslot = {(w, p, t): c5.Bool(f"in_{w}_{p}_{t}")
              for w in range(n_weeks) for p in range(n_periods) for t in teams}

    solver = c5.Solver()

    # Every period holds exactly one match.
    for w in range(n_weeks):
        for p in range(n_periods):
            # The possible matches of this period.
            matches = [play[w, p, i, j] for i in teams for j in teams if i != j]
            solver.add(c5.Or(matches))
            solver.add([c5.Not(c5.And(a, b)) for a, b in itertools.combinations(matches, 2)])

    # A team takes part in a period exactly when it is one of the two teams of its match.
    for w in range(n_weeks):
        for p in range(n_periods):
            for t in teams:
                # The matches of this period that team t plays, at home or away.
                playing = [play[w, p, t, j] for j in teams if j != t] + \
                          [play[w, p, j, t] for j in teams if j != t]
                solver.add(inslot[w, p, t] == c5.Or(playing))

    # Every team plays once a week, in exactly one of the periods of the week.
    for w in range(n_weeks):
        for t in teams:
            # The periods of week w in which team t plays.
            slots = [inslot[w, p, t] for p in range(n_periods)]
            solver.add(c5.Or(slots))
            solver.add([c5.Not(c5.And(a, b)) for a, b in itertools.combinations(slots, 2)])

    # Every team plays at most twice in the same period over the tournament, so it is never in
    # the same period in three different weeks.
    for p in range(n_periods):
        for t in teams:
            for ws in itertools.combinations(range(n_weeks), 3):
                solver.add(c5.Not(c5.And([inslot[w, p, t] for w in ws])))

    # Every two teams play each other exactly once, in some week and period, either team at home.
    for i, j in itertools.combinations(teams, 2):
        # The ways teams i and j can meet, in any week and period.
        meets = [c5.Or(play[w, p, i, j], play[w, p, j, i])
                 for w in range(n_weeks) for p in range(n_periods)]
        solver.add(c5.Or(meets))
        solver.add([c5.Not(c5.And(a, b)) for a, b in itertools.combinations(meets, 2)])

    # home[w][p] is the home team of the match in week w, period p.
    home = [[c5.Int(f"home_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]
    # away[w][p] is the away team of the match in week w, period p.
    away = [[c5.Int(f"away_{w}_{p}") for p in range(n_periods)] for w in range(n_weeks)]
    for w in range(n_weeks):
        for p in range(n_periods):
            # Each home and away entry is the team in that role in its period.
            solver.add(home[w][p] == c5.Sum(
                [c5.If(play[w, p, i, j], i, 0) for i in teams for j in teams if i != j]))
            solver.add(away[w][p] == c5.Sum(
                [c5.If(play[w, p, i, j], j, 0) for i in teams for j in teams if i != j]))

    return solver, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    status = solver.check()

    if status == c5.sat:
        model_eval = np.vectorize(solver.model().eval)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", model_eval(output))
    else:
        print("No solution:", status)

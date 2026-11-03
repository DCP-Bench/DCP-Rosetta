# csplib_026_sports_tournament_scheduling: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from pyscipopt import Model, quicksum


def create_model(instance):
    """Schedule a round-robin tournament of n teams over n-1 weeks.

    Each week has n/2 periods, and each period has two slots: the first team in
    a slot plays at home, the second plays the first team away. Every team plays
    once a week, plays at most twice in the same period over the tournament, and
    plays every other team exactly once. Teams are numbered 1 to n.

    Outputs home[w][p] and away[w][p]: the team at home and the team away in
    week w and period p (both 0-based list indices). The problem is a
    satisfaction problem, so the model has no objective.
    """
    # n_teams: the number of teams, an even number (the statement splits them
    # into n/2 periods). The statement fixes n-1 weeks and n/2 periods.
    n = instance["n_teams"]
    teams = range(1, n + 1)  # teams are numbered 1..n, as in the output
    weeks = range(n - 1)
    periods = range(n // 2)
    pairs = [(i, j) for i in teams for j in teams if i != j]  # (home team, away team)

    m = Model()
    # play[i, j, w, p] = 1 when team i plays at home against team j in week w, period p.
    # One binary per ordered pair and slot, so that "i and j meet" is a linear sum:
    # with separate home and away variables, "i and j meet" would be a product of two
    # variables, which SCIP only handles as a nonlinear constraint.
    play = {
        (i, j, w, p): m.addVar(vtype="B")
        for (i, j) in pairs
        for w in weeks
        for p in periods
    }

    # Each period of each week holds exactly one game: one home team and one away team.
    for w in weeks:
        for p in periods:
            m.addCons(quicksum(play[i, j, w, p] for (i, j) in pairs) == 1)

    # Every team plays exactly once in each week.
    for t in teams:
        for w in weeks:
            m.addCons(
                quicksum(play[t, j, w, p] + play[j, t, w, p] for j in teams if j != t for p in periods)
                == 1
            )

    # Every team plays at most twice in the same period over the whole tournament.
    # Each team plays once a week, so over the n-1 weeks it has n-1 games in total.
    for t in teams:
        for p in periods:
            m.addCons(
                quicksum(play[t, j, w, p] + play[j, t, w, p] for j in teams if j != t for w in weeks)
                <= 2
            )

    # Every team plays every other team exactly once, at home or away.
    for i in teams:
        for j in teams:
            if i < j:
                m.addCons(
                    quicksum(play[i, j, w, p] + play[j, i, w, p] for w in weeks for p in periods)
                    == 1
                )

    # The home team of a period is the team i whose game (i, j) is played there.
    # Exactly one game per period (above) makes this sum a single team.
    home = [[quicksum(i * play[i, j, w, p] for (i, j) in pairs) for p in periods] for w in weeks]
    # The away team of a period is the team j of that same game.
    away = [[quicksum(j * play[i, j, w, p] for (i, j) in pairs) for p in periods] for w in weeks]
    return m, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.hideOutput()  # no solver log
    model.optimize()

    if model.getStatus() == "optimal":  # a proven optimum, or with no objective a solution
        value = np.vectorize(lambda var: round(model.getVal(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.getStatus())

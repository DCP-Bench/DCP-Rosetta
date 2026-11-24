# csplib_026_sports_tournament_scheduling: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Sports tournament scheduling: n teams over n-1 weeks of n/2 periods; every team plays once a week, at most twice in a period, and every other team once."""
    n_teams = instance["n_teams"]                   # n: the number of teams, numbered 1 to n
    n_weeks, n_periods = n_teams - 1, n_teams // 2  # n-1 weeks, each of n/2 periods (from the statement)
    teams = range(1, n_teams + 1)
    weeks = range(n_weeks)                          # weeks and periods are numbered from 0
    periods = range(n_periods)
    pairs = [(h, a) for h in teams for a in teams if h != a]  # (home team, away team); a team never plays itself

    model = gp.Model("sports_scheduling")

    # game[w, p, h, a] is 1 when team h plays at home against team a in week w, period p, and 0 when not
    game = model.addVars([(w, p, h, a) for w in weeks for p in periods for (h, a) in pairs],
                         vtype=GRB.BINARY, name="game")

    # Each period of each week holds exactly one game.
    model.addConstrs((game.sum(w, p, "*", "*") == 1 for w in weeks for p in periods), name="one_game")

    # Each team plays exactly once a week, at home or away.
    model.addConstrs((game.sum(w, "*", t, "*") + game.sum(w, "*", "*", t) == 1
                      for w in weeks for t in teams), name="week")

    # Every team plays every other team, at home or away. The constraint says at least once;
    # with one game a week over n-1 weeks, each team plays each other team exactly once.
    model.addConstrs((game.sum("*", "*", t1, t2) + game.sum("*", "*", t2, t1) >= 1
                      for t1 in teams for t2 in teams if t1 < t2), name="meet")

    # No team plays more than twice in the same period over the tournament.
    model.addConstrs((game.sum("*", p, t, "*") + game.sum("*", p, "*", t) <= 2
                      for t in teams for p in periods), name="period")

    # home[w][p] and away[w][p]: the home and away team of the game in week w, period p (numbered 1 to n).
    home = [[gp.quicksum(h * game[w, p, h, a] for (h, a) in pairs) for p in periods] for w in weeks]
    away = [[gp.quicksum(a * game[w, p, h, a] for (h, a) in pairs) for p in periods] for w in weeks]
    return model, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded

# csplib_011_acc_basketball_schedule: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Schedule the 1997/98 Atlantic Coast Conference basketball season: 9 teams play a double round-robin over 18 dates, each pair once at each team's home, under the mirroring scheme and the rules on runs of home, away and bye dates, weekends, rivals and opponents."""
    n_teams = instance["n_teams"]  # the number of teams, 9
    n_days = instance["n_days"]    # the number of dates in the season, 18
    teams = range(n_teams)
    days = range(n_days)
    HOME, BYE, AWAY = 0, 1, 2  # codes for where a team plays on a date (the output where)

    # Team numbers, in the order of the statement: Clemson, Duke, Florida State, Georgia Tech,
    # Maryland, North Carolina, NC State, Virginia, Wake Forest.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
    # rivals[t] is the traditional rival of team t: Duke-UNC, Clem-GT, NCSt-Wake and UMD-UVA
    # from the statement. FSU has no rival (rivals[FSU] is FSU itself, and it is not used).
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]
    # scheme[d] is the date that mirrors date d: the pairs (1,8), (2,9), (3,12), (4,13), (5,14),
    # (6,15), (7,16), (10,17), (11,18) of the statement, with the dates counted from 0 here.
    scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    # Weekend dates: the second and all later even dates of the statement, which are odd here.
    weekends = [d for d in days if d % 2 == 1]

    model = gp.Model("acc_basketball")

    # 1. Mirroring. Only the first date of each mirrored pair (the base dates) gets variables:
    # game[d,i,j] is 1 when team i plays at home against team j on base date d.
    # A mirrored date has the same pairings with home and away swapped, so hosts reads
    # game[scheme[d], j, i] there instead.
    base = [d for d in days if d < scheme[d]]
    game = {(d, i, j): model.addVar(vtype=GRB.BINARY, name=f"game[{d},{i},{j}]")
            for d in base for i in teams for j in teams if i != j}

    def hosts(d, i, j):
        """1 when team i plays at home against team j on date d."""
        return game[d, i, j] if d in base else game[scheme[d], j, i]

    # home[d][i] is 1 when team i plays at home on date d; away[d][i] is 1 when it plays away;
    # bye[d][i] is 1 when it plays neither (the rest of the time).
    home = [[gp.quicksum(hosts(d, i, j) for j in teams if j != i) for i in teams] for d in days]
    away = [[gp.quicksum(hosts(d, j, i) for j in teams if j != i) for i in teams] for d in days]
    bye = [[1 - home[d][i] - away[d][i] for i in teams] for d in days]

    def meets(d, i, j):
        """1 when teams i and j play each other on date d."""
        return hosts(d, i, j) + hosts(d, j, i)

    # A team has at most one match on a date, the rest of the time a bye. This is implied by
    # the statement's dates; it is checked on base dates, and the mirrored dates follow.
    model.addConstrs((home[d][i] + away[d][i] <= 1 for d in base for i in teams), name="one_match")

    # Double round-robin: each pair plays twice, once at each home. A pair meets once on a
    # base date; the mirror of that date gives the second meeting with home and away swapped.
    model.addConstrs((gp.quicksum(meets(d, i, j) for d in base) == 1
                      for i in teams for j in teams if i < j), name="pair")

    # The rules of sections 2 to 5 are written per team, in the order of the original model
    # (row order affects how fast Gurobi finds a schedule).
    for t in teams:
        # 2. No team plays away on both of the last two dates.
        model.addConstr(away[n_days - 2][t] + away[n_days - 1][t] <= 1, name=f"final_aways[{t}]")

        # 3. Runs of matches: no more than two home matches in a row, no more than two away
        # matches in a row, no more than three away matches or byes in a row, and no more
        # than four home matches or byes in a row.
        for d in range(n_days - 2):
            model.addConstr(gp.quicksum(home[e][t] for e in range(d, d + 3)) <= 2, name=f"home_run[{t},{d}]")
            model.addConstr(gp.quicksum(away[e][t] for e in range(d, d + 3)) <= 2, name=f"away_run[{t},{d}]")
        for d in range(n_days - 3):
            model.addConstr(gp.quicksum(away[e][t] + bye[e][t] for e in range(d, d + 4)) <= 3,
                            name=f"away_or_bye_run[{t},{d}]")
        for d in range(n_days - 4):
            model.addConstr(gp.quicksum(home[e][t] + bye[e][t] for e in range(d, d + 5)) <= 4,
                            name=f"home_or_bye_run[{t},{d}]")

        # 4. Weekend pattern: over the weekends each team plays four at home, four away and has one bye.
        model.addConstr(gp.quicksum(home[d][t] for d in weekends) == 4, name=f"weekend_home[{t}]")
        model.addConstr(gp.quicksum(away[d][t] for d in weekends) == 4, name=f"weekend_away[{t}]")
        model.addConstr(gp.quicksum(bye[d][t] for d in weekends) == 1, name=f"weekend_bye[{t}]")

        # 5. First weekends: each team has a home match or a bye on at least two of the first five weekends.
        model.addConstr(gp.quicksum(home[d][t] + bye[d][t] for d in weekends[:5]) >= 2,
                        name=f"early_home_or_bye[{t}]")

    # 6. Rival matches: on the last date every team except FSU plays its rival, or plays FSU,
    # or has a bye, so it meets no other team.
    last = n_days - 1
    model.addConstrs((meets(last, t, j) == 0
                      for t in teams if t != FSU for j in teams if j not in (t, rivals[t], FSU)),
                     name="last_date_rival")

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once
    # in dates 11 to 18 (dates 10 to n_days-1 here).
    model.addConstrs((gp.quicksum(meets(d, a, b) for d in range(10, n_days)) >= 1
                      for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE))),
                     name="late_meeting")

    # 8. Opponent sequences: no team plays away at UNC and then away at Duke on consecutive
    # dates, or away at Duke and then away at UNC.
    for t in teams:
        if t not in (DUKE, UNC):
            for d in range(n_days - 1):
                model.addConstr(hosts(d, UNC, t) + hosts(d + 1, DUKE, t) <= 1, name=f"unc_then_duke[{t},{d}]")
                model.addConstr(hosts(d, DUKE, t) + hosts(d + 1, UNC, t) <= 1, name=f"duke_then_unc[{t},{d}]")
    # No team meets UNC, Duke and Wake on three consecutive dates, in any order (home or away).
    orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
              (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
    for t in teams:
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                for x, y, z in orders:
                    model.addConstr(meets(d, t, x) + meets(d + 1, t, y) + meets(d + 2, t, z) <= 2)

    # 9. Other constraints, each with its own team and date.
    # UNC plays Duke, its rival, in date 11 and in the last date.
    model.addConstr(meets(10, UNC, DUKE) == 1)
    model.addConstr(meets(last, UNC, DUKE) == 1)
    # UNC plays Clem in the second date.
    model.addConstr(meets(1, UNC, CLEM) == 1)
    # Duke has a bye in date 16.
    model.addConstr(bye[15][DUKE] == 1)
    # Wake does not play at home in date 17.
    model.addConstr(home[16][WAKE] == 0)
    # Wake has a bye in the first date.
    model.addConstr(bye[0][WAKE] == 1)
    # Clem, Duke, UMD and Wake do not play away in the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        model.addConstr(away[last][t] == 0)
    # Clem, FSU, GT and Wake do not play away in the first date.
    for t in (CLEM, FSU, GT, WAKE):
        model.addConstr(away[0][t] == 0)
    # Neither FSU nor NCSt has a bye in the last date.
    for t in (FSU, NCST):
        model.addConstr(bye[last][t] == 0)
    # UNC does not have a bye in the first date.
    model.addConstr(bye[0][UNC] == 0)

    # config[d][i] is the opponent of team i on date d, or i itself when team i has a bye.
    config = [[gp.quicksum(j * meets(d, i, j) for j in teams if j != i) + i * bye[d][i] for i in teams]
              for d in days]
    # where[d][i] is 0 when team i plays at home on date d, 1 for a bye, and 2 when it plays away.
    where = [[HOME * home[d][i] + BYE * bye[d][i] + AWAY * away[d][i] for i in teams] for d in days]
    # No objective: any schedule that meets the rules is a solution.
    return model, {"config": config, "where": where}


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

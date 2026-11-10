# csplib_011_acc_basketball_schedule: a SCIP (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install pyscipopt numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

import itertools

import numpy as np
from pyscipopt import Model, quicksum

# Team numbers 0 to 8, in the order the statement lists the teams.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)

# The rival of each team that has one (FSU has none), from the statement's rival pairs.
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM,
         NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}

# The mirroring scheme the statement gives, as pairs of 0-based date indices
# (the statement numbers dates from 1).
MIRROR = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]


def create_model(instance):
    """The 1997/98 Atlantic Coast Conference basketball timetable: 9 teams play a
    double round-robin over 18 dates, each pair meeting once at each team's home,
    with every team at home, away or on a bye on every date, and the pattern,
    weekend, rival, matchup and sequence rules of the statement. The statement
    asks for any timetable that meets these rules, so the model is a
    satisfaction problem and sets no objective.

    config[d][i] is the team that team i plays on date d, with teams numbered
    0 to 8 in the statement's order. A bye is written as the team itself: the
    statement gives no value for a bye, so this is a choice of the output.
    where[d][i] is 0 for a home match, 1 for a bye and 2 for an away match.
    """
    n_teams = instance["n_teams"]  # the number of teams (the statement has 9)
    n_days = instance["n_days"]    # the number of dates (the statement has 18); index d is the statement's date d + 1
    # The date numbers 10, 15, 16 and the slice [1:10:2] below, like MIRROR above, are
    # fixed by the statement; the rest of the model reads the sizes from the data.
    T, D = n_teams, n_days

    model = Model("csplib_011_acc_basketball_schedule")

    # home_game[d, i, j] is 1 when team i plays at home against team j on date d.
    # A team does not play itself, so the diagonal is bounded above by 0.
    home_game = model.addMatrixVar((D, T, T), vtype="B", name="home_game",
                                   ub=np.broadcast_to(1 - np.eye(T, dtype=int), (D, T, T)))
    # bye[d, i] is 1 when team i has no match on date d.
    bye = model.addMatrixVar((D, T), vtype="B", name="bye")

    # game[d, i, j] is 1 when teams i and j play each other on date d, at either venue.
    game = home_game + home_game.transpose(0, 2, 1)
    # home[d, i] is 1 when team i hosts a match on date d (sum over the opponent j).
    home = home_game.sum(axis=2)
    # away[d, i] is 1 when team i plays away on date d (sum over the host j).
    away = home_game.sum(axis=1)

    # Each team plays exactly one match, or has a bye, on each date.
    model.addMatrixCons(game.sum(axis=2) + bye == 1)

    # Double round-robin: the statement's "once at home" for each ordered pair, so
    # each pair meets twice, once at each venue. The diagonal stays 0.
    model.addMatrixCons(home_game.sum(axis=0) == 1 - np.eye(T, dtype=int))

    # Mirroring: on the two dates of each mirror pair, every team meets the same
    # opponent. Equal games with one match-or-bye per date also make the byes agree.
    for r1, r2 in MIRROR:
        model.addMatrixCons(game[r1] == game[r2])

    # No more than two home matches in a row, and no more than two away matches in a row:
    # at most two of any three consecutive dates are home (or away) matches.
    for s in range(D - 2):
        model.addMatrixCons(home[s:s + 3].sum(axis=0) <= 2)
        model.addMatrixCons(away[s:s + 3].sum(axis=0) <= 2)
    # No more than three away matches or byes in a row: at most three of any four dates.
    for s in range(D - 3):
        model.addMatrixCons((away + bye)[s:s + 4].sum(axis=0) <= 3)
    # No more than four home matches or byes in a row: at most four of any five dates.
    for s in range(D - 4):
        model.addMatrixCons((home + bye)[s:s + 5].sum(axis=0) <= 4)

    # Weekends are the statement's even-numbered dates, which are indices 1, 3, ..., D-1.
    # Over the weekends each team plays four home matches, four away and one bye.
    weekends = slice(1, D, 2)
    model.addMatrixCons(home[weekends].sum(axis=0) == 4)
    model.addMatrixCons(away[weekends].sum(axis=0) == 4)
    model.addMatrixCons(bye[weekends].sum(axis=0) == 1)

    # Each team has a home match or a bye on at least two of the first five weekends
    # (dates 2, 4, 6, 8 and 10 of the statement: indices 1, 3, 5, 7 and 9).
    model.addMatrixCons((home + bye)[1:10:2].sum(axis=0) >= 2)

    # No team plays away on both of the last two dates (indices D-2 and D-1).
    model.addMatrixCons(away[D - 2:].sum(axis=0) <= 1)

    # On the last date, every team except FSU plays its rival, plays FSU, or has a bye.
    # A team has at most one match a day, so requiring one of these to hold is the same as
    # requiring its match, if it has one, to be against one of these opponents.
    for team, rival in RIVAL.items():
        model.addCons(game[D - 1, team, rival] + game[D - 1, team, FSU] + bye[D - 1, team] >= 1)

    # Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once on dates 11 to 18
    # (indices 10 to D-1), at either venue.
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        model.addCons(quicksum(game[d, a, b] for d in range(10, D)) >= 1)

    # No team plays away against UNC on one date and away against Duke on the next
    # date, in either order.
    for d in range(D - 1):
        model.addMatrixCons(home_game[d, UNC] + home_game[d + 1, DUKE] <= 1)
        model.addMatrixCons(home_game[d, DUKE] + home_game[d + 1, UNC] <= 1)

    # No team plays UNC, Duke and Wake on three consecutive dates, in any order and at
    # either venue: for each of the six orders, the three games cannot all be present.
    for a, b, c in itertools.permutations([UNC, DUKE, WAKE]):
        for d in range(D - 2):
            model.addMatrixCons(game[d, :, a] + game[d + 1, :, b] + game[d + 2, :, c] <= 2)

    # UNC plays Duke on the last date and on date 11 (indices D-1 and 10), and plays Clem
    # on the second date (index 1).
    model.addCons(game[D - 1, UNC, DUKE] == 1)
    model.addCons(game[10, UNC, DUKE] == 1)
    model.addCons(game[1, UNC, CLEM] == 1)
    # Duke has a bye on date 16 (index 15).
    model.addCons(bye[15, DUKE] == 1)
    # Wake does not play at home on date 17 (index 16).
    model.addCons(home[16, WAKE] == 0)
    # Wake has a bye on the first date (index 0).
    model.addCons(bye[0, WAKE] == 1)
    # Clem, Duke, UMD and Wake do not play away on the last date.
    for team in [CLEM, DUKE, UMD, WAKE]:
        model.addCons(away[D - 1, team] == 0)
    # Clem, FSU, GT and Wake do not play away on the first date.
    for team in [CLEM, FSU, GT, WAKE]:
        model.addCons(away[0, team] == 0)
    # Neither FSU nor NCSt has a bye on the last date.
    for team in [FSU, NCST]:
        model.addCons(bye[D - 1, team] == 0)
    # UNC does not have a bye on the first date.
    model.addCons(bye[0, UNC] == 0)

    # config[d, i] is the number of the opponent of team i on date d: the sum of the
    # opponent numbers weighted by the game indicators, plus i times its bye indicator.
    config = (game * np.arange(T)).sum(axis=2) + bye * np.arange(T)
    # 0 for a home match, 1 for a bye, 2 for an away match.
    where = 2 * away + bye

    return model, {"config": config, "where": where}


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

# csplib_011_acc_basketball_schedule: a Z3 (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install z3-solver numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

import z3


def create_model(instance):
    """Find a timetable for the 1997/98 Atlantic Coast Conference basketball season: a
    double round-robin for 9 teams over 18 dates, where each team plays every other team
    once at home and once away, subject to nine sets of additional constraints."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates in the season
    teams = range(n_teams)
    days = range(n_days)

    # The nine teams.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    # Each team's traditional rival. FSU has none, so it is listed as its own rival.
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    # Mirroring scheme of Nemhauser and Trick, as pairs of dates.
    mirror_pairs = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15),
                    (9, 16), (10, 17)]
    # The first and all odd-numbered dates are weekdays, so the weekend fixtures are the
    # second, fourth, and later dates.
    weekends = [d for d in days if d % 2 == 1]
    # the last date of the season
    last = n_days - 1

    # play[d][t][u] is true when team t meets team u on date d. A team meeting itself has a bye.
    play = [[[z3.Bool(f"play_{d}_{t}_{u}") for u in teams] for t in teams] for d in days]
    # home[d][t] is true when team t plays at home on date d.
    home = [[z3.Bool(f"home_{d}_{t}") for t in teams] for d in days]
    # away[d][t] is true when team t plays away on date d.
    away = [[z3.Bool(f"away_{d}_{t}") for t in teams] for d in days]

    # team t has a bye on date d
    def bye(d, t):
        return play[d][t][t]

    # The rules of the timetable.
    solver = z3.Solver()

    for d in days:
        for t in teams:
            # Each team plays one opponent on each date, or has a bye.
            solver.add(z3.PbEq([(play[d][t][u], 1) for u in teams], 1))
            # On each date a team plays at home, plays away, or has a bye.
            solver.add(z3.PbEq([(home[d][t], 1), (away[d][t], 1), (bye(d, t), 1)], 1))
            for u in teams:
                if u > t:
                    # If team t plays team u then team u plays team t.
                    solver.add(play[d][t][u] == play[d][u][t])
                if u != t:
                    # When two teams play each other, one is home and the other away.
                    solver.add(z3.Implies(play[d][t][u], home[d][t] == away[d][u]))
                    solver.add(z3.Implies(play[d][t][u], away[d][t] == home[d][u]))

    # Each team plays each other team once at its own home, and so once away.
    for t in teams:
        for opponent in teams:
            if t != opponent:
                solver.add(z3.PbEq(
                    [(z3.And(play[d][t][opponent], home[d][t]), 1) for d in days], 1))

    # Mirroring: the two dates of a pair have the same opponents, with home and away
    # swapped. A bye stays a bye.
    for d1, d2 in mirror_pairs:
        for t in teams:
            for u in teams:
                solver.add(play[d1][t][u] == play[d2][t][u])
            solver.add(home[d1][t] == away[d2][t])
            solver.add(away[d1][t] == home[d2][t])

    for t in teams:
        # No team plays away on both of the last two dates.
        solver.add(z3.AtMost(away[last - 1][t], away[last][t], 1))

        # Home, away and bye runs: no more than two home matches or two away matches in a row,
        # no more than three away matches or byes in a row, and no more than four home matches
        # or byes in a row.
        for d in days:
            if d + 3 <= n_days:
                solver.add(z3.AtMost(*[home[k][t] for k in range(d, d + 3)], 2))
                solver.add(z3.AtMost(*[away[k][t] for k in range(d, d + 3)], 2))
            if d + 4 <= n_days:
                solver.add(z3.AtMost(
                    *[z3.Or(away[k][t], bye(k, t)) for k in range(d, d + 4)], 3))
            if d + 5 <= n_days:
                solver.add(z3.AtMost(
                    *[z3.Or(home[k][t], bye(k, t)) for k in range(d, d + 5)], 4))

        # Weekend pattern: over the weekends each team plays four at home, four away and has one bye.
        solver.add(z3.PbEq([(home[d][t], 1) for d in weekends], 4))
        solver.add(z3.PbEq([(away[d][t], 1) for d in weekends], 4))
        solver.add(z3.PbEq([(bye(d, t), 1) for d in weekends], 1))

        # First weekends: each team has a home match or a bye on at least two of the first five weekends.
        solver.add(z3.AtLeast(*[z3.Or(home[d][t], bye(d, t)) for d in weekends[:5]], 2))

        # Rival matches: on the last date every team except FSU plays its rival, unless it plays
        # FSU or has a bye.
        if t != FSU:
            solver.add(z3.Or(play[last][t][rivals[t]], play[last][t][FSU], bye(last, t)))

    # Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each occur at least once on
    # dates 11 to 18.
    for team, opponent in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        solver.add(z3.Or([play[d][team][opponent] for d in range(10, n_days)]))

    # Opponent sequences: no team plays away against UNC and Duke on two consecutive dates, and
    # no team (other than UNC, Duke and Wake) plays UNC, Duke and Wake on three consecutive dates,
    # in any order, at home or away.
    for t in teams:
        if t != DUKE and t != UNC:
            for d in range(n_days - 1):
                for first, second in [(UNC, DUKE), (DUKE, UNC)]:
                    solver.add(z3.Not(z3.And(
                        play[d][t][first], away[d][t],
                        play[d + 1][t][second], away[d + 1][t])))
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                for a, b, c in [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                                (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]:
                    solver.add(z3.Not(z3.And(
                        play[d][t][a], play[d + 1][t][b], play[d + 2][t][c])))

    # Fixed requests from the statement.
    # UNC plays its rival Duke on date 11 and on the last date.
    solver.add(play[10][UNC][DUKE])
    solver.add(play[last][UNC][DUKE])
    # UNC plays Clemson on the second date.
    solver.add(play[1][UNC][CLEM])
    # Duke has a bye on date 16.
    solver.add(bye(15, DUKE))
    # Wake does not play at home on date 17.
    solver.add(z3.Not(home[16][WAKE]))
    # Wake has a bye on the first date.
    solver.add(bye(0, WAKE))
    # Clemson, Duke, Maryland and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        solver.add(z3.Not(away[last][t]))
    # Clemson, Florida State, Georgia Tech and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        solver.add(z3.Not(away[0][t]))
    # Florida State and NC State have no bye on the last date.
    for t in (FSU, NCSt):
        solver.add(z3.Not(bye(last, t)))
    # UNC has no bye on the first date.
    solver.add(z3.Not(bye(0, UNC)))

    # config[d][t] is the opponent of team t on date d, or team t itself on a bye.
    config = [[z3.Sum([z3.If(play[d][t][u], u, 0) for u in teams]) for t in teams]
              for d in days]
    # where[d][t] is 0 when team t plays at home on date d, 1 on a bye and 2 when it plays away.
    where = [[z3.If(home[d][t], 0, z3.If(away[d][t], 2, 1)) for t in teams]
             for d in days]

    return solver, {"config": config, "where": where}


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

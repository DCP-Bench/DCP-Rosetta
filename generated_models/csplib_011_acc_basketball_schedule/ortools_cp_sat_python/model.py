# csplib_011_acc_basketball_schedule: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from itertools import permutations

from ortools.sat.python import cp_model


def create_model(instance):
    """Find a timetable for the 1997/98 Atlantic Coast Conference basketball season: a
    double round-robin for 9 teams over 18 dates, where each team plays every other team
    once at home and once away, subject to nine sets of additional constraints."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates

    # Team names, rivals and the date pairing come from the problem statement.
    # Index d is date d + 1 of the statement.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(n_teams)
    # RIVALS[t] is the traditional rival of team t. FSU has no rival and is skipped in rule 6.
    RIVALS = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]
    # MIRROR[d] is the date paired with date d.
    MIRROR = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    # the three ways a team can be placed on a date
    HOME, BYE, AWAY = 0, 1, 2

    # the dates
    days = range(n_days)
    # the teams
    teams = range(n_teams)
    # the weekend dates are the second, fourth, ... dates; the others are weekdays
    weekends = [d for d in days if d % 2 == 1]
    # the last date
    last = n_days - 1

    model = cp_model.CpModel()

    # plays[d][t][u] is true when team t meets team u on date d. A team meeting itself is a bye.
    plays = [[[model.new_bool_var(f"plays_{d}_{t}_{u}") for u in teams] for t in teams] for d in days]
    # home[d][t] is true when team t plays at home on date d
    home = [[model.new_bool_var(f"home_{d}_{t}") for t in teams] for d in days]
    # away[d][t] is true when team t plays away on date d
    away = [[model.new_bool_var(f"away_{d}_{t}") for t in teams] for d in days]
    # bye[d][t] is true when team t has no match on date d
    bye = [[plays[d][t][t] for t in teams] for d in days]

    # config[d][t] is the opponent of team t on date d, or t itself on a bye
    config = [[model.new_int_var(0, n_teams - 1, f"config_{d}_{t}") for t in teams] for d in days]
    # where[d][t] is HOME, BYE or AWAY for team t on date d
    where = [[model.new_int_var(0, 2, f"where_{d}_{t}") for t in teams] for d in days]

    # Each team meets exactly one opponent per date, and the match is the same for both teams.
    # A team is at home, away or on a bye, and where and config report it.
    for d in days:
        for t in teams:
            model.add_exactly_one(plays[d][t])
            model.add(config[d][t] == sum(u * plays[d][t][u] for u in teams))
            model.add_exactly_one([home[d][t], bye[d][t], away[d][t]])
            model.add(where[d][t] == HOME * home[d][t] + BYE * bye[d][t] + AWAY * away[d][t])
            for u in teams:
                model.add(plays[d][t][u] == plays[d][u][t])
                # Two teams that meet have one home match and one away match.
                if u != t:
                    model.add(home[d][t] == away[d][u]).only_enforce_if(plays[d][t][u])
                    model.add(away[d][t] == home[d][u]).only_enforce_if(plays[d][t][u])

    # Double round-robin: each team meets every other team once at its own home.
    for t in teams:
        for u in teams:
            if u != t:
                # at_home[d] is true when team t plays team u at home on date d
                at_home = []
                for d in days:
                    home_game = model.new_bool_var(f"home_game_{d}_{t}_{u}")
                    model.add_bool_and([plays[d][t][u], home[d][t]]).only_enforce_if(home_game)
                    model.add_bool_or([~plays[d][t][u], ~home[d][t]]).only_enforce_if(~home_game)
                    at_home.append(home_game)
                model.add(sum(at_home) == 1)

    # Rule 1, mirroring: dates d and MIRROR[d] have the same opponents, with home and away swapped.
    for d in days:
        m = MIRROR[d]
        for t in teams:
            for u in teams:
                model.add(plays[d][t][u] == plays[m][t][u])
            model.add(home[d][t] == away[m][t])
            model.add(away[d][t] == home[m][t])

    # Rule 2: no team plays away on both of the last two dates.
    for t in teams:
        model.add(away[last - 1][t] + away[last][t] <= 1)

    # Rule 3: home, away and bye runs. Each window of consecutive dates is limited.
    for t in teams:
        for d in range(n_days - 2):
            # at most two home matches in a row
            model.add(sum(home[e][t] for e in range(d, d + 3)) <= 2)
            # at most two away matches in a row
            model.add(sum(away[e][t] for e in range(d, d + 3)) <= 2)
        for d in range(n_days - 3):
            # at most three away matches or byes in a row
            model.add(sum(away[e][t] + bye[e][t] for e in range(d, d + 4)) <= 3)
        for d in range(n_days - 4):
            # at most four home matches or byes in a row
            model.add(sum(home[e][t] + bye[e][t] for e in range(d, d + 5)) <= 4)

    # Rule 4, weekend pattern: over the weekends, four home matches, four away matches and one bye.
    for t in teams:
        model.add(sum(home[d][t] for d in weekends) == 4)
        model.add(sum(away[d][t] for d in weekends) == 4)
        model.add(sum(bye[d][t] for d in weekends) == 1)

    # Rule 5, first weekends: a home match or a bye on at least two of the first five weekends.
    for t in teams:
        model.add(sum(home[d][t] + bye[d][t] for d in weekends[:5]) >= 2)

    # Rule 6, rival matches: on the last date, each team except FSU plays its rival,
    # unless it plays FSU or has a bye.
    for t in teams:
        if t != FSU:
            model.add_bool_or([plays[last][t][RIVALS[t]], plays[last][t][FSU], bye[last][t]])

    # Rule 7, constrained matches: these pairings meet at least once on dates 11 to 18.
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        model.add(sum(plays[d][a][b] for d in range(10, n_days)) >= 1)

    # Rule 8, opponent sequences.
    for t in teams:
        for d in range(n_days - 1):
            if t not in (DUKE, UNC):
                # Apart from Duke and UNC, no team plays away against UNC and Duke
                # on two consecutive dates, in either order.
                for a, b in [(UNC, DUKE), (DUKE, UNC)]:
                    model.add_bool_or([~plays[d][t][a], ~away[d][t], ~plays[d + 1][t][b], ~away[d + 1][t]])
        for d in range(n_days - 2):
            if t not in (UNC, DUKE, WAKE):
                # Apart from UNC, Duke and Wake, no team plays UNC, Duke and Wake
                # on three consecutive dates, in any order.
                for a, b, c in permutations([UNC, DUKE, WAKE]):
                    model.add_bool_or([~plays[d][t][a], ~plays[d + 1][t][b], ~plays[d + 2][t][c]])

    # Rule 9, other requests.
    model.add(plays[10][UNC][DUKE] == 1)  # UNC plays Duke on date 11 ...
    model.add(plays[last][UNC][DUKE] == 1)  # ... and on the last date
    model.add(plays[1][UNC][CLEM] == 1)  # UNC plays Clemson on the second date
    model.add(bye[15][DUKE] == 1)  # Duke has a bye on date 16
    model.add(home[16][WAKE] == 0)  # Wake does not play at home on date 17
    model.add(bye[0][WAKE] == 1)  # Wake has a bye on the first date
    for t in (CLEM, DUKE, UMD, WAKE):
        model.add(away[last][t] == 0)  # these teams do not play away on the last date
    for t in (CLEM, FSU, GT, WAKE):
        model.add(away[0][t] == 0)  # these teams do not play away on the first date
    for t in (FSU, NCST):
        model.add(bye[last][t] == 0)  # FSU and NC State have no bye on the last date
    model.add(bye[0][UNC] == 0)  # UNC has no bye on the first date

    return model, {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

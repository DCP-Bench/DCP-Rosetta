# csplib_011_acc_basketball_schedule: a cvc5 (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install cvc5 numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

import itertools

import cvc5.pythonic as c5


def exactly_one(options):
    """Constraints saying that exactly one of the options is true."""
    pairs = itertools.combinations(options, 2)
    return [c5.Or(options)] + [c5.Or(c5.Not(a), c5.Not(b)) for a, b in pairs]


def create_model(instance):
    """Find a timetable for the 1997/98 Atlantic Coast Conference basketball season: a
    double round-robin for 9 teams over 18 dates, where each team plays every other team
    once at home and once away, subject to nine sets of additional constraints."""
    n_days = instance["n_days"]    # the number of dates
    n_teams = instance["n_teams"]  # the number of teams
    days = range(1, n_days + 1)    # dates are numbered from 1, as in the statement
    teams = range(n_teams)
    last = n_days                  # the last date

    # Team numbers, in the order of the statement
    CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = teams
    # RIVAL[t] is the traditional rival of team t. FSU has none.
    RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
    # Pairs of dates on which each team meets the same opponent, with home and away swapped.
    MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]

    # host[d][t][u] is true when team t plays at home against team u on date d
    host = {d: {t: {u: c5.Bool(f"host_{d}_{t}_{u}") for u in teams if u != t} for t in teams} for d in days}
    # bye[d][t] is true when team t has no game on date d
    bye = {d: {t: c5.Bool(f"bye_{d}_{t}") for t in teams} for d in days}

    # home(d, t): team t plays at home on date d
    def home(d, t):
        return c5.Or([host[d][t][u] for u in teams if u != t])

    # away(d, t): team t plays away on date d
    def away(d, t):
        return c5.Or([host[d][u][t] for u in teams if u != t])

    # plays(d, t, u): teams t and u play each other on date d
    def plays(d, t, u):
        return c5.Or(host[d][t][u], host[d][u][t])

    solver = c5.Solver()

    # Double round-robin: each team plays each other team once at home and once away.
    for t in teams:
        for u in teams:
            if u != t:
                solver.add(exactly_one([host[d][t][u] for d in days]))

    # Each team plays one game or has a bye on each date.
    for d in days:
        for t in teams:
            solver.add(exactly_one([bye[d][t]] + [plays(d, t, u) for u in teams if u != t]))

    # Each team has n_days - 2 * (n_teams - 1) byes, the dates left over after its games.
    for t in teams:
        solver.add(c5.Sum([c5.If(bye[d][t], 1, 0) for d in days]) == n_days - 2 * (n_teams - 1))
    # Each date has n_teams % 2 byes and n_teams // 2 games, and each game has one home team.
    for d in days:
        solver.add(c5.Sum([c5.If(bye[d][t], 1, 0) for t in teams]) == n_teams % 2)
        solver.add(c5.Sum([c5.If(host[d][t][u], 1, 0) for t in teams for u in teams if u != t])
                   == n_teams // 2)

    # Mirroring: on both dates of a pair, each team meets the same opponent, with home and away
    # swapped, and has a bye on both dates or on neither.
    for r1, r2 in MIRROR:
        for t in teams:
            solver.add(bye[r1][t] == bye[r2][t])
            for u in teams:
                if u != t:
                    solver.add(host[r1][t][u] == host[r2][u][t])

    # The second, fourth, ... dates are weekends.
    weekends = [d for d in days if d % 2 == 0]
    # Weekend pattern: over the weekends each team plays four games at home, four away, and has one bye.
    for t in teams:
        solver.add(c5.Sum([c5.If(home(d, t), 1, 0) for d in weekends]) == 4)
        solver.add(c5.Sum([c5.If(away(d, t), 1, 0) for d in weekends]) == 4)
        solver.add(c5.Sum([c5.If(bye[d][t], 1, 0) for d in weekends]) == 1)

    # First weekends: each team has a home game or a bye on at least two of the first five weekends.
    for t in teams:
        solver.add(c5.Sum([c5.If(c5.Or(home(d, t), bye[d][t]), 1, 0) for d in weekends[:5]]) >= 2)

    # No team has more than two away games in a row.
    for t in teams:
        for start in range(1, n_days - 1):
            solver.add(c5.Not(c5.And([away(d, t) for d in range(start, start + 3)])))
    # No team has more than two home games in a row.
    for t in teams:
        for start in range(1, n_days - 1):
            solver.add(c5.Not(c5.And([home(d, t) for d in range(start, start + 3)])))
    # No team has more than three away games or byes in a row.
    for t in teams:
        for start in range(1, n_days - 2):
            solver.add(c5.Not(c5.And([c5.Or(away(d, t), bye[d][t]) for d in range(start, start + 4)])))
    # No team has more than four home games or byes in a row.
    for t in teams:
        for start in range(1, n_days - 3):
            solver.add(c5.Not(c5.And([c5.Or(home(d, t), bye[d][t]) for d in range(start, start + 5)])))

    # No team plays away on both of the last two dates.
    for t in teams:
        solver.add(c5.Not(c5.And(away(last - 1, t), away(last, t))))

    # Rival matches: on the last date each team plays its rival, unless it plays FSU or has a bye.
    for t, rival in RIVAL.items():
        solver.add(c5.Or(plays(last, t, rival), plays(last, t, FSU), bye[last][t]))

    # Constrained matches: each of these pairs meets at least once on dates 11 to the last date.
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        solver.add(c5.Or([plays(d, a, b) for d in range(11, n_days + 1)]))

    # Opponent sequence: no team plays away against UNC and Duke on consecutive dates, in either
    # order. UNC and Duke themselves are left out.
    for d in range(1, n_days):
        for t in teams:
            for x, y in [(UNC, DUKE), (DUKE, UNC)]:
                if t not in (x, y):
                    solver.add(c5.Not(c5.And(host[d][x][t], host[d + 1][y][t])))
    # Opponent sequence: no team other than UNC, Duke and Wake meets all three of them on three
    # consecutive dates, in any order.
    trio = [UNC, DUKE, WAKE]
    for d in range(1, n_days - 1):
        for t in teams:
            if t not in trio:
                for a, b, c in itertools.permutations(trio):
                    solver.add(c5.Not(c5.And(plays(d, t, a), plays(d + 1, t, b), plays(d + 2, t, c))))

    # UNC plays Duke on the last date and on date 11, and plays Clem on date 2.
    solver.add(plays(last, UNC, DUKE), plays(11, UNC, DUKE), plays(2, UNC, CLEM))
    # Duke has a bye on date 16.
    solver.add(bye[16][DUKE])
    # Wake does not play at home on date 17, and has a bye on date 1.
    solver.add(c5.Not(home(17, WAKE)), bye[1][WAKE])
    # Clem, Duke, UMD and Wake do not play away on the last date.
    solver.add([c5.Not(away(last, t)) for t in (CLEM, DUKE, UMD, WAKE)])
    # Clem, FSU, GT and Wake do not play away on date 1.
    solver.add([c5.Not(away(1, t)) for t in (CLEM, FSU, GT, WAKE)])
    # FSU and NCSt have no bye on the last date.
    solver.add([c5.Not(bye[last][t]) for t in (FSU, NCST)])
    # UNC has no bye on date 1.
    solver.add(c5.Not(bye[1][UNC]))

    # config[d][i] is the team that team i plays on date d, or i itself on a bye
    config = [[c5.Sum([c5.If(bye[d][i], i, 0)] + [c5.If(plays(d, i, j), j, 0) for j in teams if j != i])
               for i in teams]
              for d in days]
    # where[d][i] is 0 for a home game, 1 for a bye and 2 for an away game
    where = [[c5.If(home(d, i), 0, c5.If(bye[d][i], 1, 2)) for i in teams] for d in days]

    return solver, {"config": config, "where": where}


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

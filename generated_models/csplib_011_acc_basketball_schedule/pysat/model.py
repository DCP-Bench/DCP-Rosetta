# csplib_011_acc_basketball_schedule: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from itertools import permutations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Find a double round-robin timetable for the 1997/98 Atlantic Coast Conference basketball
    teams: over the dates, each team plays every other team once at home and once away,
    subject to nine sets of rules on the schedule."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates in the schedule

    # The rules below name these teams and dates, so they fit only the 9 teams and 18 dates
    # of the ACC problem.
    assert n_teams == 9 and n_days == 18, "the rules below are written for the ACC problem"

    # Clemson, Duke, Florida State, Georgia Tech, Maryland, North Carolina, North Carolina
    # State, Virginia and Wake Forest, numbered from 0 in that order.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    # Traditional rivals. Florida State has no rival.
    rival_pairs = [(DUKE, UNC), (CLEM, GT), (NCSt, WAKE), (UMD, UVA)]
    rival = {}
    for first, second in rival_pairs:
        rival[first], rival[second] = second, first
    # Mirroring: pairs of dates on which each team plays the same opponent, once at home and
    # once away. The dates are numbered from 1, as in the statement.
    mirror_pairs = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]
    days = range(n_days)
    teams = range(n_teams)
    # Weekend dates are the even-numbered dates of the statement, which are odd indices here.
    weekends = [d for d in days if d % 2 == 1]
    last = n_days - 1  # the last date

    pool = IDPool()

    HOME, BYE, AWAY = 0, 1, 2  # the values of where

    # config[d][t]: the team that team t plays on date d; t itself means a bye
    config = [[Integer(f"config{d}_{t}", 0, n_teams - 1, vpool=pool) for t in teams] for d in days]
    # where[d][t]: HOME, BYE or AWAY, whether team t plays at home, has a bye or plays away on date d
    where = [[Integer(f"where{d}_{t}", 0, 2, vpool=pool) for t in teams] for d in days]

    # Conditions on date d for team t: it plays team u, it plays at home, it has a bye, or it
    # plays away.
    def plays(d, t, u):
        return config[d][t].equals(u)

    def home(d, t):
        return where[d][t].equals(HOME)

    def bye(d, t):
        return where[d][t].equals(BYE)

    def away(d, t):
        return where[d][t].equals(AWAY)

    engine = IntegerEngine(vars=[v for row in config + where for v in row], vpool=pool)

    # On each date the pairings form a permutation: each team is met by exactly one team,
    # itself for a bye.
    for d in days:
        engine.add_alldifferent(config[d])

    cnf = engine.clausify()

    # Matches are mutual: if t plays u on a date, then u plays t on that date.
    for d in days:
        for t in teams:
            for u in teams:
                cnf.append([-plays(d, t, u), plays(d, u, t)])

    # On each date, two teams that play each other are one at home and one away, and a team
    # plays itself exactly when it has a bye.
    for d in days:
        for t in teams:
            cnf.append([-plays(d, t, t), bye(d, t)])
            cnf.append([plays(d, t, t), -bye(d, t)])
            for u in teams:
                if u != t:
                    cnf.append([-plays(d, t, u), -home(d, t), away(d, u)])
                    cnf.append([-plays(d, t, u), home(d, t), -away(d, u)])
                    cnf.append([-plays(d, t, u), -away(d, t), home(d, u)])
                    cnf.append([-plays(d, t, u), away(d, t), -home(d, u)])

    # Double round-robin: each team meets every other team exactly once at its own home.
    for t in teams:
        for u in teams:
            if u != t:
                # home_dates: the dates on which t plays at home against u
                home_dates = []
                for d in days:
                    hosts = pool.id(("home_against", d, t, u))
                    cnf.append([-hosts, plays(d, t, u)])
                    cnf.append([-hosts, home(d, t)])
                    cnf.append([hosts, -plays(d, t, u), -home(d, t)])
                    home_dates.append(hosts)
                cnf.extend(CardEnc.equals(lits=home_dates, bound=1, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # 1. Mirroring: on the two dates of a pair, every team plays the same opponent, at home on
    # one date and away on the other. A bye stays a bye.
    for first, second in mirror_pairs:
        d1, d2 = first - 1, second - 1
        for t in teams:
            for u in teams:
                cnf.append([-plays(d1, t, u), plays(d2, t, u)])
                cnf.append([plays(d1, t, u), -plays(d2, t, u)])
            cnf.append([-home(d1, t), away(d2, t)])
            cnf.append([home(d1, t), -away(d2, t)])
            cnf.append([-away(d1, t), home(d2, t)])
            cnf.append([away(d1, t), -home(d2, t)])
            cnf.append([-bye(d1, t), bye(d2, t)])
            cnf.append([bye(d1, t), -bye(d2, t)])

    for t in teams:
        # 2. No two final aways: no team plays away on both of the last two dates.
        cnf.append([-away(last - 1, t), -away(last, t)])

        # 3. Home, away and bye runs.
        for d in range(n_days - 2):
            # No more than two home matches in a row.
            cnf.append([-home(d, t), -home(d + 1, t), -home(d + 2, t)])
            # No more than two away matches in a row.
            cnf.append([-away(d, t), -away(d + 1, t), -away(d + 2, t)])
        for d in range(n_days - 3):
            # No more than three away matches or byes in a row: one of every four dates is a home date.
            cnf.append([home(d + k, t) for k in range(4)])
        for d in range(n_days - 4):
            # No more than four home matches or byes in a row: one of every five dates is an away date.
            cnf.append([away(d + k, t) for k in range(5)])

        # 4. Weekend pattern: of the weekends, four at home, four away and one bye.
        cnf.extend(CardEnc.equals(lits=[home(d, t) for d in weekends], bound=4, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
        cnf.extend(CardEnc.equals(lits=[away(d, t) for d in weekends], bound=4, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)
        cnf.extend(CardEnc.equals(lits=[bye(d, t) for d in weekends], bound=1, vpool=pool,
                                  encoding=EncType.seqcounter).clauses)

        # 5. First weekends: home matches or byes on at least two of the first five weekends.
        cnf.extend(CardEnc.atleast(lits=[-away(d, t) for d in weekends[:5]], bound=2, vpool=pool,
                                   encoding=EncType.seqcounter).clauses)

        # 6. Rival matches: on the last date, every team except Florida State plays its rival,
        # unless it plays Florida State or has a bye.
        if t != FSU:
            cnf.append([plays(last, t, rival[t]), plays(last, t, FSU), bye(last, t)])

    # 7. Constrained matches: Wake Forest and Georgia Tech each play North Carolina and Duke
    # at least once in dates 11 to 18.
    for t, u in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        cnf.append([plays(d, t, u) for d in range(10, n_days)])

    # 8. Opponent sequences.
    for t in teams:
        if t not in (DUKE, UNC):
            # No team plays away against North Carolina and Duke on two consecutive dates.
            for d in range(n_days - 1):
                for first, second in [(UNC, DUKE), (DUKE, UNC)]:
                    cnf.append([-plays(d, t, first), -away(d, t),
                                -plays(d + 1, t, second), -away(d + 1, t)])
        if t not in (UNC, DUKE, WAKE):
            # No team plays North Carolina, Duke and Wake Forest on three consecutive dates,
            # in any order and home or away.
            for d in range(n_days - 2):
                for order in permutations([UNC, DUKE, WAKE]):
                    cnf.append([-plays(d + k, t, order[k]) for k in range(3)])

    # 9. Other constraints.
    cnf.append([plays(10, UNC, DUKE)])      # North Carolina plays Duke on date 11 ...
    cnf.append([plays(last, UNC, DUKE)])    # ... and on the last date
    cnf.append([plays(1, UNC, CLEM)])       # North Carolina plays Clemson on date 2
    cnf.append([bye(15, DUKE)])             # Duke has a bye on date 16
    cnf.append([-home(16, WAKE)])           # Wake Forest does not play at home on date 17
    cnf.append([bye(0, WAKE)])              # Wake Forest has a bye on date 1
    for t in (CLEM, DUKE, UMD, WAKE):
        cnf.append([-away(last, t)])        # Clemson, Duke, Maryland and Wake Forest do not play away on the last date
    for t in (CLEM, FSU, GT, WAKE):
        cnf.append([-away(0, t)])           # Clemson, Florida State, Georgia Tech and Wake Forest do not play away on date 1
    for t in (FSU, NCSt):
        cnf.append([-bye(last, t)])         # Florida State and NC State have no bye on the last date
    cnf.append([-bye(0, UNC)])              # North Carolina has no bye on date 1

    return cnf, {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

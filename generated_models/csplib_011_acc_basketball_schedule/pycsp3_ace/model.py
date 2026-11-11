# csplib_011_acc_basketball_schedule: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from pycsp3 import *


def create_model(instance):
    """The 1997/98 Atlantic Coast Conference basketball teams play a double round-robin schedule over
    18 dates: each team plays each other once at home and once away. The odd dates are weekday
    fixtures and the even dates weekend fixtures. The schedule also follows the statement's further
    constraints: mirroring, no two final aways, home/away/bye patterns, the weekend pattern, first
    weekends, rival matches, constrained matches, opponent sequences and other constraints."""
    n_teams = instance["n_teams"]   # the number of teams
    n_days = instance["n_days"]     # the number of dates

    # The teams are numbered from 0 in the order of the statement. The dates are numbered from 0 too,
    # and the comments name them as the statement does, from 1: statement date k is index k - 1.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(n_teams)

    # The values of where: the statement codes a home match 0, a bye 1 and an away match 2.
    HOME, BYE, AWAY = 0, 1, 2

    weekends = range(2 - 1, n_days, 2)   # the weekend fixtures: the statement's even dates 2, 4, ...
    first_five_weekends = weekends[:5]   # the first five weekends of the statement
    last = n_days - 1                    # the last date
    last_but_one = n_days - 2            # the date before the last
    late_dates = range(11 - 1, n_days)   # the statement's dates 11 to 18

    # The mirroring scheme of the statement: each pair (r1, r2) of dates.
    mirroring_scheme = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]

    # The traditional rival of each team; FSU has none.
    rivals = {CLEM: GT, GT: CLEM, DUKE: UNC, UNC: DUKE, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}

    # config[d][i] is the team that team i plays on date d; it is i itself when team i has a bye.
    config = VarArray(size=[n_days, n_teams], dom=range(n_teams))
    # where[d][i] is HOME, BYE or AWAY: where team i plays on date d.
    where = VarArray(size=[n_days, n_teams], dom={HOME, BYE, AWAY})

    satisfy(
        # On each date every team meets at most one opponent: no two teams name the same opponent.
        (AllDifferent(config[d]) for d in range(n_days)),

        # A match is symmetric: if team i plays team j, then team j plays team i.
        (config[d][config[d][i]] == i
         for d in range(n_days)
         for i in range(n_teams)),

        # A team has a bye exactly when it is its own opponent.
        ((config[d][i] == i) == (where[d][i] == BYE)
         for d in range(n_days)
         for i in range(n_teams)),

        # The two teams of a match: one plays at home, the other away.
        (where[d][config[d][i]] + where[d][i] == HOME + AWAY
         for d in range(n_days)
         for i in range(n_teams)),

        # Each pair of teams meets twice, and each team is at home against the other once.
        (Count(config[:, i], value=j) == 2
         for i in range(n_teams)
         for j in range(n_teams)
         if i != j),
        (Sum(And(config[d][i] == j, where[d][i] == HOME) for d in range(n_days)) == 1
         for i in range(n_teams)
         for j in range(n_teams)
         if i != j),

        # Mirroring: for each pair (r1, r2) of the scheme, a team has the same opponent on dates r1 and r2,
        # and a team at home on one of the two dates is away on the other (a bye is then a bye on both dates).
        (config[r1 - 1][i] == config[r2 - 1][i]
         for r1, r2 in mirroring_scheme
         for i in range(n_teams)),
        (where[r1 - 1][i] + where[r2 - 1][i] == HOME + AWAY
         for r1, r2 in mirroring_scheme
         for i in range(n_teams)),

        # No two final aways: no team plays away on both of the last two dates.
        (Or(where[last_but_one][i] != AWAY, where[last][i] != AWAY)
         for i in range(n_teams)),

        # No more than two away matches in a row: no three consecutive dates are all away.
        (Sum(where[d + k][i] == AWAY for k in range(3)) <= 2
         for i in range(n_teams)
         for d in range(n_days - 2)),

        # No more than two home matches in a row: no three consecutive dates are all home.
        (Sum(where[d + k][i] == HOME for k in range(3)) <= 2
         for i in range(n_teams)
         for d in range(n_days - 2)),

        # No more than three away matches or byes in a row: no four consecutive dates without a home match.
        (Sum(where[d + k][i] != HOME for k in range(4)) <= 3
         for i in range(n_teams)
         for d in range(n_days - 3)),

        # No more than four home matches or byes in a row: no five consecutive dates without an away match.
        (Sum(where[d + k][i] != AWAY for k in range(5)) <= 4
         for i in range(n_teams)
         for d in range(n_days - 4)),

        # Weekend pattern: over the weekends each team plays four matches at home, four away and has one bye.
        (Cardinality([where[d][i] for d in weekends], occurrences={HOME: 4, AWAY: 4, BYE: 1})
         for i in range(n_teams)),

        # First weekends: each team has a home match or a bye on at least two of the first five weekends.
        (Sum(where[d][i] != AWAY for d in first_five_weekends) >= 2
         for i in range(n_teams)),

        # Rival matches: on the last date every team except FSU plays its rival, unless it plays FSU or has a bye.
        (config[last][team] in {rival, FSU, team}
         for team, rival in rivals.items()),

        # Constrained matches: Wake and UNC, Wake and Duke, GT and UNC, and GT and Duke each meet in dates 11 to 18.
        (Sum(config[d][a] == b for d in late_dates) >= 1
         for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]),

        # Opponent sequences: no team plays away against UNC on one date and away against Duke on the next
        # date, or the other way round.
        (Or(config[d][i] != UNC, where[d][i] != AWAY, config[d + 1][i] != DUKE, where[d + 1][i] != AWAY)
         for i in range(n_teams)
         for d in range(n_days - 1)),
        (Or(config[d][i] != DUKE, where[d][i] != AWAY, config[d + 1][i] != UNC, where[d + 1][i] != AWAY)
         for i in range(n_teams)
         for d in range(n_days - 1)),

        # No team plays three consecutive dates against UNC, Duke and Wake in some order (home or away does
        # not matter). UNC, Duke and Wake themselves are left out: their own bye would count as one of the three.
        (Table(scope=[config[d][i], config[d + 1][i], config[d + 2][i]],
               conflicts=[(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                          (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)])
         for i in range(n_teams) if i not in (UNC, DUKE, WAKE)
         for d in range(n_days - 2)),

        # UNC plays its rival Duke on the last date and on date 11.
        config[last][UNC] == DUKE,
        config[11 - 1][UNC] == DUKE,
        # UNC plays Clem on the second date.
        config[2 - 1][UNC] == CLEM,
        # Duke has a bye on date 16.
        config[16 - 1][DUKE] == DUKE,
        # Wake does not play at home on date 17.
        where[17 - 1][WAKE] != HOME,
        # Wake has a bye on the first date.
        config[1 - 1][WAKE] == WAKE,
        # UNC does not have a bye on the first date.
        where[1 - 1][UNC] != BYE,

        # Clem, Duke, UMD and Wake do not play away on the last date.
        (where[last][t] != AWAY for t in [CLEM, DUKE, UMD, WAKE]),

        # Clem, FSU, GT and Wake do not play away on the first date.
        (where[1 - 1][t] != AWAY for t in [CLEM, FSU, GT, WAKE]),

        # Neither FSU nor NCSt has a bye on the last date.
        (where[last][t] != BYE for t in [FSU, NCST]),
    )

    return {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("config", "=")
        for row in outputs["config"]:
            print(values(row))
    else:
        print("No solution:", status())

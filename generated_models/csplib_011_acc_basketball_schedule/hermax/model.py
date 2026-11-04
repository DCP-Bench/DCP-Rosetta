# csplib_011_acc_basketball_schedule: a hermax (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install hermax`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from itertools import permutations

from hermax.model import Model

# The nine teams of the 1997/98 Atlantic Coast Conference, numbered in the order the
# problem statement lists them (fixed by the problem, not by the instance).
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)

# RIVAL[t] is the traditional rival of team t. FSU has no rival.
RIVAL = {CLEM: GT, GT: CLEM, DUKE: UNC, UNC: DUKE, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}

# The codes of where[d][i], as the problem statement gives them.
HOME, BYE, AWAY = 0, 1, 2

# The mirroring scheme (Nemhauser and Trick) on the 1-based dates (1, 8), (2, 9), ...,
# written with 0-based dates: (0, 7), (1, 8), ...
MIRROR_PAIRS = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]


def create_model(instance):
    """Schedule a double round-robin of the nine ACC basketball teams over 18 dates.

    Each team plays every other team once at home and once away. Each date is a
    weekday or a weekend fixture, and the schedule must follow the mirroring scheme,
    the home/away/bye patterns, the weekend and rival rules, and the opponent-sequence
    and fixed-date rules of the problem statement."""
    n = instance["n_teams"]    # n: the number of teams (9)
    days = instance["n_days"]  # days: the number of dates (18)
    last = days - 1            # the 0-based index of the last date

    # The second, fourth, ... dates are weekend fixtures (0-based: the odd indices).
    weekends = [d for d in range(days) if d % 2 == 1]

    m = Model()
    # opp[d][i] is the team that team i plays on date d; it is i itself when team i has a bye
    opp = m.int_matrix("opp", days, n, 0, n - 1)
    # loc[d][i] is HOME, BYE or AWAY: where team i is on date d
    loc = m.int_matrix("loc", days, n, HOME, AWAY)

    # Opponents pair up: if team i plays team j on a date, team j plays team i on it.
    # A bye is exactly when a team is its own opponent.
    for d in range(days):
        for i in range(n):
            m &= (~(opp[d][i] == i) | (loc[d][i] == BYE))
            m &= (~(loc[d][i] == BYE) | (opp[d][i] == i))
            for j in range(n):
                if j != i:
                    m &= (~(opp[d][i] == j) | (opp[d][j] == i))
                    # two teams that play each other: one is at home and the other is away
                    m &= (~(opp[d][i] == j) | (loc[d][i] == HOME) | (loc[d][j] == HOME))
                    m &= (~(opp[d][i] == j) | ~(loc[d][i] == HOME) | ~(loc[d][j] == HOME))

    # Double round-robin: each team hosts each other team exactly once. (The away game
    # against that team is then implied, because the other team hosts it.)
    for t in range(n):
        for o in range(n):
            if o != t:
                hosted = []
                for d in range(days):
                    # hosts[d] is true when team t hosts team o on date d
                    hosts = m.bool()
                    m &= (~hosts | (opp[d][t] == o))
                    m &= (~hosts | (loc[d][t] == HOME))
                    m &= (hosts | ~(opp[d][t] == o) | ~(loc[d][t] == HOME))
                    hosted.append(hosts)
                m &= (sum(hosted) == 1)

    # 1. Mirroring: the two dates of a pair have the same opponent for every team.
    for d, e in MIRROR_PAIRS:
        for i in range(n):
            m &= (opp[d][i] == opp[e][i])
            # (Implied, kept to help the solver: with the same opponent on both dates,
            #  hosting each team exactly once forces home on one date and away on the
            #  other; a bye stays a bye. The codes HOME=0 and AWAY=2 add up to 2, and
            #  BYE=1 added to itself gives 2 too.)
            m &= (loc[d][i] + loc[e][i] == 2)

    for t in range(n):
        # 2. No team plays away on both of the last two dates.
        m &= (~(loc[last - 1][t] == AWAY) | ~(loc[last][t] == AWAY))

        # 3. Home/away/bye patterns, read as windows of consecutive dates.
        #    No more than two home matches in a row, and no more than two away matches in a row.
        for d in range(days - 2):
            m &= (sum(loc[d + k][t] == HOME for k in range(3)) <= 2)
            m &= (sum(loc[d + k][t] == AWAY for k in range(3)) <= 2)
        #    No more than three away matches or byes in a row: four dates hold a home match.
        for d in range(days - 3):
            m &= (sum(loc[d + k][t] != HOME for k in range(4)) <= 3)
        #    No more than four home matches or byes in a row: five dates hold an away match.
        for d in range(days - 4):
            m &= (sum(loc[d + k][t] != AWAY for k in range(5)) <= 4)

        # 4. Of the weekends, each team plays four at home, four away, and has one bye.
        m &= (sum(loc[d][t] == HOME for d in weekends) == 4)
        m &= (sum(loc[d][t] == AWAY for d in weekends) == 4)
        m &= (sum(loc[d][t] == BYE for d in weekends) == 1)

        # 5. First weekends: home matches or byes on at least two of the first five weekends.
        m &= (sum(loc[d][t] != AWAY for d in weekends[:5]) >= 2)

        # 6. Rival matches: on the last date every team except FSU plays its rival, unless it
        #    plays FSU or has a bye.
        if t != FSU:
            m &= ((opp[last][t] == RIVAL[t]) | (opp[last][t] == FSU) | (loc[last][t] == BYE))

    # 7. Constrained matches: these pairs meet at least once in dates 11 to 18.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        m &= (sum(opp[d][a] == b for d in range(10, days)) >= 1)

    # 8. Opponent sequences. No team plays away against UNC and against Duke on two
    #    consecutive dates, in either order (skipped for UNC and Duke, for whom it is vacuous:
    #    a team cannot play itself).
    #    No team plays UNC, Duke and Wake on three consecutive dates, in any order,
    #    whatever the home/away (skipped for UNC, Duke and Wake, for whom it is vacuous).
    for t in range(n):
        if t not in (UNC, DUKE):
            for d in range(days - 1):
                for x, y in ((UNC, DUKE), (DUKE, UNC)):
                    m &= (~(opp[d][t] == x) | ~(loc[d][t] == AWAY)
                          | ~(opp[d + 1][t] == y) | ~(loc[d + 1][t] == AWAY))
        if t not in (UNC, DUKE, WAKE):
            for d in range(days - 2):
                for x, y, z in permutations((UNC, DUKE, WAKE)):
                    m &= (~(opp[d][t] == x) | ~(opp[d + 1][t] == y) | ~(opp[d + 2][t] == z))

    # 9. Other constraints, with the dates 0-based (date 11 is index 10).
    # UNC plays its rival Duke on the last date and on date 11.
    m &= (opp[10][UNC] == DUKE)
    m &= (opp[last][UNC] == DUKE)
    # UNC plays Clemson on the second date.
    m &= (opp[1][UNC] == CLEM)
    # Duke has a bye on date 16.
    m &= (loc[15][DUKE] == BYE)
    # Wake does not play at home on date 17.
    m &= (loc[16][WAKE] != HOME)
    # Wake has a bye on the first date.
    m &= (loc[0][WAKE] == BYE)
    # Clemson, Duke, Maryland and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        m &= (loc[last][t] != AWAY)
    # Clemson, FSU, Georgia Tech and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        m &= (loc[0][t] != AWAY)
    # Neither FSU nor NC State has a bye on the last date.
    for t in (FSU, NCST):
        m &= (loc[last][t] != BYE)
    # UNC does not have a bye on the first date.
    m &= (loc[0][UNC] != BYE)

    # Satisfaction problem: no objective. config[d][i] is the opponent of team i on date d
    # (its own number for a bye); where[d][i] is HOME, BYE or AWAY.
    return m, {"config": opp, "where": loc}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    result = model.solve()

    if result.ok:  # optimum, sat, or a best solution found before a time limit
        for name, output in outputs.items():
            print(name, "=", result[output])
    else:
        print("No solution:", result.status)

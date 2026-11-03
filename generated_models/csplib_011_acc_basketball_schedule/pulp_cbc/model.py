# csplib_011_acc_basketball_schedule: a PuLP (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install pulp numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from itertools import product

import pulp


def create_model(instance):
    """Schedule the 1997/98 Atlantic Coast Conference basketball season: a double round-robin
    in which each team plays every other team once at home and once away over the dates,
    subject to the rules of the problem."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates in the season
    teams = range(n_teams)
    days = range(n_days)

    # The team names, rivals and mirroring pairs come from the problem statement.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = teams
    # rivals[t] is the traditional rival of team t. FSU has none, and rule 6 leaves it out.
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    # scheme[d] is the date that mirrors date d, with dates numbered from 0.
    scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    # The weekends are the second, fourth, ... dates of the season; the others are weekdays.
    weekends = [d for d in days if d % 2 == 1]
    # The three ways a team can stand on a date: at home, on a bye, or away.
    HOME, BYE, AWAY = 0, 1, 2
    last = n_days - 1

    # Each mirrored pair of dates has one base date, the earlier one. The other date is read from it.
    base = [d for d in days if d < scheme[d]]

    problem = pulp.LpProblem("acc_basketball_schedule", pulp.LpMinimize)  # satisfaction

    # host_var[d][i][j] is 1 when team i hosts team j on base date d.
    host_var = {d: [[pulp.LpVariable(f"host_{d}_{i}_{j}", cat="Binary") if i != j else None
                     for j in teams] for i in teams] for d in base}
    # bye_var[d][i] is 1 when team i has a bye on base date d.
    bye_var = {d: [pulp.LpVariable(f"bye_{d}_{i}", cat="Binary") for i in teams] for d in base}

    # 1 when team i hosts team j on date d. A mirrored date takes its matches from its base date.
    def host(d, i, j):
        return host_var[d][i][j] if d in host_var else host_var[scheme[d]][j][i]

    # 1 when team i has a bye on date d.
    def bye(d, i):
        return bye_var[d][i] if d in bye_var else bye_var[scheme[d]][i]

    # 1 when teams i and j meet on date d, wherever the match is played. For i == j this is a bye.
    def plays(d, i, j):
        if i == j:
            return bye(d, i)
        return host(d, i, j) + host(d, j, i)

    # 1 when team i plays at home on date d.
    def home(d, i):
        return pulp.lpSum(host(d, i, j) for j in teams if j != i)

    # 1 when team i plays away on date d.
    def away(d, i):
        return pulp.lpSum(host(d, j, i) for j in teams if j != i)

    # Whether a season of home, bye and away dates obeys rules 2 to 5.
    def allowed(pattern):
        # How many of the dates in the window have one of the given kinds.
        def count(window, kinds):
            return sum(1 for w in window if w in kinds)
        # 2. No team plays away on both last dates.
        if count(pattern[-2:], (AWAY,)) > 1:
            return False
        for d in range(n_days - 2):
            # 3. No more than two home matches, or two away matches, in a row.
            if count(pattern[d:d + 3], (HOME,)) > 2 or count(pattern[d:d + 3], (AWAY,)) > 2:
                return False
        for d in range(n_days - 3):
            # 3. No more than three away matches or byes in a row.
            if count(pattern[d:d + 4], (AWAY, BYE)) > 3:
                return False
        for d in range(n_days - 4):
            # 3. No more than four home matches or byes in a row.
            if count(pattern[d:d + 5], (HOME, BYE)) > 4:
                return False
        # 4. Over the weekends: four home matches, four away matches and one bye.
        on_weekends = [pattern[d] for d in weekends]
        if (on_weekends.count(HOME), on_weekends.count(AWAY), on_weekends.count(BYE)) != (4, 4, 1):
            return False
        # 5. Home matches or byes on at least two of the first five weekends.
        if count([pattern[d] for d in weekends[:5]], (HOME, BYE)) < 2:
            return False
        return True

    # Every season that obeys rules 2 to 5 and the mirroring of the dates.
    patterns = []
    for choice in product((HOME, BYE, AWAY), repeat=len(base)):
        pattern = [None] * n_days
        for d, w in zip(base, choice):
            pattern[d] = w
            pattern[scheme[d]] = 2 - w  # the mirrored date swaps home and away, and a bye stays a bye
        if allowed(pattern):
            patterns.append(pattern)

    # follows[i][p] is 1 when team i follows pattern p over the season.
    follows = [[pulp.LpVariable(f"follows_{i}_{p}", cat="Binary") for p in range(len(patterns))]
               for i in teams]

    # 1 when the pattern team i follows has the given placement on date d.
    def pattern_says(d, i, kind):
        return pulp.lpSum(var for p, var in enumerate(follows[i]) if patterns[p][d] == kind)

    # On each base date every team hosts one opponent, visits one, or has a bye.
    for d in base:
        for i in teams:
            problem += home(d, i) + away(d, i) + bye(d, i) == 1

    # Each team hosts every other team exactly once, and so visits it once away.
    for i in teams:
        for j in teams:
            if i != j:
                problem += pulp.lpSum(host(d, i, j) for d in days) == 1

    # Each team follows exactly one pattern, and its home and bye dates are those of the pattern.
    for i in teams:
        problem += pulp.lpSum(follows[i]) == 1
        for d in base:
            problem += home(d, i) == pattern_says(d, i, HOME)
            problem += bye(d, i) == pattern_says(d, i, BYE)
            # A team hosts an opponent only on a date it is at home and the opponent is away.
            for j in teams:
                if j != i:
                    problem += host(d, i, j) <= pattern_says(d, i, HOME)
                    problem += host(d, i, j) <= pattern_says(d, j, AWAY)

    # No two teams follow the same pattern: they would be at home or away together on every date,
    # and could never meet.
    for p in range(len(patterns)):
        problem += pulp.lpSum(follows[i][p] for i in teams) <= 1
    # On each base date one team has a bye, and the other teams split evenly between home and away.
    for d in base:
        problem += pulp.lpSum(pattern_says(d, i, BYE) for i in teams) == 1
        problem += pulp.lpSum(pattern_says(d, i, HOME) for i in teams) == (n_teams - 1) // 2

    # 6. On the last date every team except FSU plays its rival, unless it plays FSU or has a bye,
    #    so it plays no other team.
    for i in teams:
        if i != FSU:
            for j in teams:
                if j not in (rivals[i], FSU, i):
                    problem += plays(last, i, j) == 0

    # 7. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once from date 11 on.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        problem += pulp.lpSum(plays(d, a, b) for d in range(10, n_days)) >= 1

    # 8. Opponent sequences.
    for t in teams:
        if t not in (DUKE, UNC):
            # No team plays away against UNC and then away against Duke on consecutive dates, or the
            # other way round.
            for d in range(n_days - 1):
                problem += host(d, UNC, t) + host(d + 1, DUKE, t) <= 1
                problem += host(d, DUKE, t) + host(d + 1, UNC, t) <= 1
        if t not in (UNC, DUKE, WAKE):
            # No team meets UNC, Duke and Wake on three consecutive dates, in any order.
            orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                      (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
            for d in range(n_days - 2):
                for a, b, c in orders:
                    problem += plays(d, t, a) + plays(d + 1, t, b) + plays(d + 2, t, c) <= 2

    # 9. Other constraints.
    problem += plays(10, UNC, DUKE) == 1     # UNC plays its rival Duke on date 11
    problem += plays(last, UNC, DUKE) == 1   # and on the last date
    problem += plays(1, UNC, CLEM) == 1      # UNC plays Clem on the second date
    problem += bye(15, DUKE) == 1            # Duke has a bye on date 16
    problem += home(16, WAKE) == 0           # Wake does not play at home on date 17
    problem += bye(0, WAKE) == 1             # Wake has a bye on the first date
    for t in (CLEM, DUKE, UMD, WAKE):        # these do not play away on the last date
        problem += away(last, t) == 0
    for t in (CLEM, FSU, GT, WAKE):          # these do not play away on the first date
        problem += away(0, t) == 0
    for t in (FSU, NCSt):                    # neither has a bye on the last date
        problem += bye(last, t) == 0
    problem += bye(0, UNC) == 0              # UNC does not have a bye on the first date

    # The opponent of team i on date d, which is i itself on a bye.
    config = [[pulp.lpSum(j * plays(d, i, j) for j in teams) for i in teams] for d in days]
    # The place of team i on date d: at home, on a bye, or away.
    where = [[HOME * home(d, i) + BYE * bye(d, i) + AWAY * away(d, i) for i in teams]
             for d in days]
    return problem, {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    problem, outputs = create_model(instances[index])
    problem.solve(pulp.PULP_CBC_CMD(msg=False))

    if problem.status == pulp.LpStatusOptimal:
        value = np.vectorize(lambda var: round(pulp.value(var)))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", pulp.LpStatus[problem.status])

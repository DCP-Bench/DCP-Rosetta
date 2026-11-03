# csplib_011_acc_basketball_schedule: an Exact (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install exact numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from itertools import permutations

from exact import Exact


def create_model(instance):
    """Schedule the 1997/98 Atlantic Coast Conference basketball season: over the dates, each
    team plays every other team once at home and once away, subject to the rules below."""
    n_teams = instance["n_teams"]  # number of teams
    n_days = instance["n_days"]    # number of dates in the season
    teams = range(n_teams)
    days = range(n_days)
    last = n_days - 1              # the last date

    # Clemson, Duke, Florida State, Georgia Tech, Maryland, North Carolina, North Carolina State,
    # Virginia and Wake Forest.
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = teams
    HOME, BYE, AWAY = 0, 1, 2  # the three ways a team can be placed on a date
    # rivals[t] is the traditional rival of team t. Florida State has none.
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    # Nemhauser and Trick's mirroring scheme: each pair of dates has the same pairings, with home
    # and away swapped.
    mirrored = [(0, 7), (1, 8), (2, 11), (3, 12), (4, 13), (5, 14), (6, 15), (9, 16), (10, 17)]
    # The second, fourth, ... and eighteenth dates are weekends; the others are weekdays.
    weekends = [d for d in days if d % 2 == 1]

    solver = Exact()

    # meet_name(d, a, b) is 1 when teams a and b play each other on date d. One variable covers
    # both teams, so they always agree on the match.
    def meet_name(d, a, b):
        return f"meet_{d}_{min(a, b)}_{max(a, b)}"

    # hosts_name(d, t, o) is 1 when team t plays team o at home on date d.
    def hosts_name(d, t, o):
        return f"hosts_{d}_{t}_{o}"

    # plays(d, t, o) is 1 when team t meets team o on date d. For o equal to t it is the bye
    # variable: 1 when team t has a bye on date d.
    def plays(d, t, o):
        return f"bye_{d}_{t}" if o == t else meet_name(d, t, o)

    # The statement fixes these values on particular dates. A variable listed here has only that
    # value.
    fixed = {
        meet_name(10, UNC, DUKE): 1,   # UNC plays Duke on date 11
        meet_name(last, UNC, DUKE): 1, # UNC plays Duke on the last date
        meet_name(1, UNC, CLEM): 1,    # UNC plays Clemson on the second date
        f"bye_15_{DUKE}": 1,           # Duke has a bye on date 16
        f"at_home_16_{WAKE}": 0,       # Wake Forest does not play at home on date 17
        f"bye_0_{WAKE}": 1,            # Wake Forest has a bye on the first date
        f"bye_0_{UNC}": 0,             # UNC does not have a bye on the first date
    }
    fixed.update({f"away_{last}_{t}": 0 for t in (CLEM, DUKE, UMD, WAKE)})  # no away game on the last date
    fixed.update({f"away_0_{t}": 0 for t in (CLEM, FSU, GT, WAKE)})         # no away game on the first date
    fixed.update({f"bye_{last}_{t}": 0 for t in (FSU, NCSt)})               # no bye on the last date

    # Exact identifies its variables by name.
    # A variable the statement fixes has that single value. Every other variable is 0 or 1.
    def declare(name):
        lo, hi = (fixed[name],) * 2 if name in fixed else (0, 1)
        solver.addVariable(name, lo, hi)

    for d in days:
        for a in teams:
            for b in range(a + 1, n_teams):
                declare(meet_name(d, a, b))
            for o in teams:
                if o != a:
                    declare(hosts_name(d, a, o))
            for kind in ("bye", "at_home", "away"):
                declare(f"{kind}_{d}_{a}")

    # config[d][t] is the opponent of team t on date d, or team t itself on a bye.
    config = [[f"config_{d}_{t}" for t in teams] for d in days]
    # where[d][t] is HOME, BYE or AWAY for team t on date d.
    where = [[f"where_{d}_{t}" for t in teams] for d in days]
    for d in days:
        for t in teams:
            solver.addVariable(config[d][t], 0, n_teams - 1)
            solver.addVariable(where[d][t], 0, 2)

    for d in days:
        for t in teams:
            # Each team plays exactly one opponent on each date, or has a bye.
            solver.addConstraint([(1, plays(d, t, o)) for o in teams], True, 1, True, 1)

            # When two teams meet on a date, one hosts the other.
            for o in teams:
                if o > t:
                    solver.addConstraint([(1, meet_name(d, t, o)), (-1, hosts_name(d, t, o)),
                                          (-1, hosts_name(d, o, t))], True, 0, True, 0)
            # A team is at home on a date when it hosts someone, and away when someone hosts it.
            solver.addConstraint([(1, f"at_home_{d}_{t}")] +
                                 [(-1, hosts_name(d, t, o)) for o in teams if o != t],
                                 True, 0, True, 0)
            solver.addConstraint([(1, f"away_{d}_{t}")] +
                                 [(-1, hosts_name(d, o, t)) for o in teams if o != t],
                                 True, 0, True, 0)

            # config and where report the opponent and the placement of team t on date d.
            solver.addConstraint([(1, config[d][t])] + [(-o, plays(d, t, o)) for o in teams],
                                 True, 0, True, 0)
            solver.addConstraint([(1, where[d][t]), (-BYE, f"bye_{d}_{t}"), (-AWAY, f"away_{d}_{t}")],
                                 True, 0, True, 0)

    # Each team hosts each other team once over the season: every pair plays once at each venue.
    for t in teams:
        for o in teams:
            if o != t:
                solver.addConstraint([(1, hosts_name(d, t, o)) for d in days], True, 1, True, 1)

    # Mirroring: the dates of a pair have the same pairings, with home and away swapped. A bye
    # stays a bye.
    for r1, r2 in mirrored:
        for t in teams:
            solver.addConstraint([(1, f"bye_{r1}_{t}"), (-1, f"bye_{r2}_{t}")], True, 0, True, 0)
            for o in teams:
                if o > t:
                    solver.addConstraint([(1, meet_name(r1, t, o)), (-1, meet_name(r2, t, o))],
                                         True, 0, True, 0)
                if o != t:
                    solver.addConstraint([(1, hosts_name(r1, t, o)), (-1, hosts_name(r2, o, t))],
                                         True, 0, True, 0)

    # No team plays away on both of the last two dates.
    for t in teams:
        solver.addConstraint([(1, f"away_{n_days - 2}_{t}"), (1, f"away_{last}_{t}")],
                             False, 0, True, 1)

    # Home, away and bye runs over consecutive dates.
    for t in teams:
        # No team has more than two home matches in a row, or more than two away matches in a row.
        for d in range(n_days - 2):
            solver.addConstraint([(1, f"at_home_{k}_{t}") for k in range(d, d + 3)],
                                 False, 0, True, 2)
            solver.addConstraint([(1, f"away_{k}_{t}") for k in range(d, d + 3)],
                                 False, 0, True, 2)
        # No team has more than three away matches or byes in a row.
        for d in range(n_days - 3):
            solver.addConstraint([(1, f"{kind}_{k}_{t}") for k in range(d, d + 4)
                                  for kind in ("away", "bye")], False, 0, True, 3)
        # No team has more than four home matches or byes in a row.
        for d in range(n_days - 4):
            solver.addConstraint([(1, f"{kind}_{k}_{t}") for k in range(d, d + 5)
                                  for kind in ("at_home", "bye")], False, 0, True, 4)

    # Weekend pattern: over the weekends, each team plays four matches at home, four away and has
    # one bye.
    for t in teams:
        for kind, count in (("at_home", 4), ("away", 4), ("bye", 1)):
            solver.addConstraint([(1, f"{kind}_{d}_{t}") for d in weekends], True, count, True, count)

    # First weekends: each team has a home match or a bye on at least two of the first five weekends.
    for t in teams:
        solver.addConstraint([(1, f"{kind}_{d}_{t}") for d in weekends[:5]
                              for kind in ("at_home", "bye")], True, 2)

    # Rival matches: on the last date every team except Florida State plays its rival, unless it
    # plays Florida State or has a bye. These three cases exclude each other, so at least one holds.
    for t in teams:
        if t != FSU:
            solver.addConstraint([(1, plays(last, t, rivals[t])), (1, plays(last, t, FSU)),
                                  (1, plays(last, t, t))], True, 1)

    # Constrained matches: Wake Forest-UNC, Wake Forest-Duke, Georgia Tech-UNC and Georgia
    # Tech-Duke each take place at least once on dates 11 to 18.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        solver.addConstraint([(1, meet_name(d, a, b)) for d in range(10, n_days)], True, 1)

    # Opponent sequences.
    for t in teams:
        # Apart from Duke and UNC, no team plays away against UNC and Duke on two consecutive
        # dates, in either order.
        if t not in (DUKE, UNC):
            for d in range(n_days - 1):
                for first, second in ((UNC, DUKE), (DUKE, UNC)):
                    solver.addConstraint([(1, meet_name(d, t, first)), (1, f"away_{d}_{t}"),
                                          (1, meet_name(d + 1, t, second)),
                                          (1, f"away_{d + 1}_{t}")], False, 0, True, 3)
        # Apart from UNC, Duke and Wake Forest, no team meets UNC, Duke and Wake Forest on three
        # consecutive dates, in any order, home or away.
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                for x, y, z in permutations((UNC, DUKE, WAKE)):
                    solver.addConstraint([(1, meet_name(d, t, x)), (1, meet_name(d + 1, t, y)),
                                          (1, meet_name(d + 2, t, z))], False, 0, True, 2)

    return solver, {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    solver, outputs = create_model(instances[index])
    solver.runFull()  # with an objective, searches until no better solution exists

    if solver.hasSolution():
        for name, output in outputs.items():
            values = solver.getLastSolutionFor(list(np.ravel(output)))
            print(name, "=", np.reshape(values, np.shape(output)))
    else:
        print("No solution")

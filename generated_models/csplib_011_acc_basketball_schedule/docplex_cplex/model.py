# csplib_011_acc_basketball_schedule: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from docplex.mp.model import Model


def create_model(instance):
    """ACC basketball schedule: a timetable for the 9 teams of the 1997/98 Atlantic Coast
    Conference, a double round-robin (each team plays each other once at home and once away)
    over 18 dates, subject to the mirroring, pattern, rival and fixture constraints."""
    n_teams = instance["n_teams"]  # number of teams
    n_days = instance["n_days"]    # number of dates
    teams = range(n_teams)
    days = range(n_days)

    # Teams are numbered in the order of the statement. rivals[t] is the traditional rival of
    # team t (FSU has none, so its entry is itself).
    CLEM, DUKE, FSU, GT, UMD, UNC, NCSt, UVA, WAKE = range(9)
    rivals = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCSt]
    # Mirroring: date d and date scheme[d] have the same pairings with home and away swapped.
    scheme = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
    weekends = [d for d in days if d % 2 == 1]  # the even dates of the statement (dates count from 0 here)
    last = n_days - 1  # the last date

    model = Model("acc_basketball_schedule")
    # A satisfaction problem: ask CPLEX to look for a feasible schedule first.
    model.parameters.emphasis.mip = 1

    # The schedule is decided on the first date of each mirrored pair only; the other date
    # repeats it with home and away swapped. This keeps the model within the Community
    # Edition's 1000-variable limit (9 dates x 72 ordered pairs instead of 18 x 9 x 9).
    base_days = [d for d in days if d < scheme[d]]
    hosts_base = {(d, i, j): model.binary_var(name=f"hosts_{d}_{i}_{j}")
                  for d in base_days for i in teams for j in teams if i != j}

    def hosts(d, i, j):
        """1 when team i plays at home against team j on date d."""
        if d in base_days:
            return hosts_base[d, i, j]
        return hosts_base[scheme[d], j, i]

    def home(d, t):
        """1 when team t plays at home on date d."""
        return model.sum(hosts(d, t, j) for j in teams if j != t)

    def away(d, t):
        """1 when team t plays away on date d."""
        return model.sum(hosts(d, j, t) for j in teams if j != t)

    def meets(d, t, j):
        """1 when team t plays team j on date d, at home or away."""
        return hosts(d, t, j) + hosts(d, j, t)

    # A team plays at most one match per date; otherwise it has a bye.
    for d in base_days:
        for t in teams:
            model.add_constraint(home(d, t) + away(d, t) <= 1)

    # Double round-robin: each team hosts each other team exactly once. With mirroring, i
    # hosts j once over the season exactly when the two meet once over the base dates.
    for i in teams:
        for j in teams:
            if i < j:
                model.add_constraint(model.sum(meets(d, i, j) for d in base_days) == 1)

    # Implied by the round-robin, stated to help the solver: each team plays 8 opponents on
    # the 9 base dates, so it has exactly one bye there; and the 36 meetings fill the 9 base
    # dates, at most 4 matches each, so every base date has exactly 4 matches.
    for t in teams:
        model.add_constraint(model.sum(home(d, t) + away(d, t) for d in base_days)
                             == n_teams - 1)
    for d in base_days:
        model.add_constraint(model.sum(home(d, t) for t in teams) == (n_teams - 1) // 2)

    # 2. No two final aways: no team plays away on both of the last two dates.
    for t in teams:
        model.add_constraint(away(last - 1, t) + away(last, t) <= 1)

    # 3. Home/away/bye patterns.
    for t in teams:
        for d in range(n_days - 2):
            # No more than two home matches in a row.
            model.add_constraint(model.sum(home(e, t) for e in range(d, d + 3)) <= 2)
            # No more than two away matches in a row.
            model.add_constraint(model.sum(away(e, t) for e in range(d, d + 3)) <= 2)
        for d in range(n_days - 3):
            # No more than three away matches or byes in a row: a home match within any
            # four consecutive dates.
            model.add_constraint(model.sum(home(e, t) for e in range(d, d + 4)) >= 1)
        for d in range(n_days - 4):
            # No more than four home matches or byes in a row: an away match within any five
            # consecutive dates.
            model.add_constraint(model.sum(away(e, t) for e in range(d, d + 5)) >= 1)

    # 4. Weekend pattern: of the nine weekends each team plays four at home, four away and
    # (so) one bye.
    for t in teams:
        model.add_constraint(model.sum(home(d, t) for d in weekends) == 4)
        model.add_constraint(model.sum(away(d, t) for d in weekends) == 4)

    # 5. First weekends: home matches or byes on at least two of the first five weekends,
    # that is at most three away matches there.
    for t in teams:
        model.add_constraint(model.sum(away(d, t) for d in weekends[:5]) <= 3)

    # 6. Rival matches: on the last date every team except FSU plays its rival, or plays FSU,
    # or has a bye.
    for t in teams:
        if t != FSU:
            model.add_constraint(meets(last, t, rivals[t]) + meets(last, t, FSU)
                                 + 1 - home(last, t) - away(last, t) >= 1)

    # 7. Constrained matches: Wake-UNC, Wake-Duke, GT-UNC and GT-Duke each meet at least once
    # in dates 11 to 18.
    for a, b in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        model.add_constraint(model.sum(meets(d, a, b) for d in range(10, n_days)) >= 1)

    # 8. Opponent sequences. A team meets a given opponent only on the two dates of one
    # mirrored pair, which are 7 or 9 dates apart, so it never meets the same opponent within
    # three consecutive dates; it also meets one opponent per date. Under that:
    # - "no away match against UNC then away against Duke on the next date, or Duke then UNC"
    #   is the same as at most one away match against UNC or Duke over two consecutive dates;
    # - "no three consecutive dates against UNC, Duke and Wake, in any order" is the same as
    #   at most two matches against those three over three consecutive dates.
    for t in teams:
        if t not in (DUKE, UNC):
            for d in range(n_days - 1):
                model.add_constraint(model.sum(hosts(e, o, t) for e in (d, d + 1)
                                               for o in (UNC, DUKE)) <= 1)
        if t not in (UNC, DUKE, WAKE):
            for d in range(n_days - 2):
                model.add_constraint(model.sum(meets(e, t, o) for e in (d, d + 1, d + 2)
                                               for o in (UNC, DUKE, WAKE)) <= 2)

    # 9. Other constraints.
    # UNC plays its rival Duke on the last date and on date 11.
    model.add_constraint(meets(10, UNC, DUKE) == 1)
    model.add_constraint(meets(last, UNC, DUKE) == 1)
    # UNC plays Clem on the second date.
    model.add_constraint(meets(1, UNC, CLEM) == 1)
    # Duke has a bye on date 16.
    model.add_constraint(home(15, DUKE) + away(15, DUKE) == 0)
    # Wake does not play at home on date 17.
    model.add_constraint(home(16, WAKE) == 0)
    # Wake has a bye on the first date.
    model.add_constraint(home(0, WAKE) + away(0, WAKE) == 0)
    # Clem, Duke, UMD and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        model.add_constraint(away(last, t) == 0)
    # Clem, FSU, GT and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        model.add_constraint(away(0, t) == 0)
    # Neither FSU nor NCSt has a bye on the last date.
    for t in (FSU, NCSt):
        model.add_constraint(home(last, t) + away(last, t) == 1)
    # UNC does not have a bye on the first date.
    model.add_constraint(home(0, UNC) + away(0, UNC) == 1)

    # config[d][t] is the opponent of team t on date d, or t itself on a bye.
    # where[d][t] is 0 for home, 1 for a bye and 2 for away: 1 - home + away.
    config = [[t + model.sum((j - t) * meets(d, t, j) for j in teams if j != t)
               for t in teams] for d in days]
    where = [[1 - home(d, t) + away(d, t) for t in teams] for d in days]

    return model, {"config": config, "where": where}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solution = model.solve()

    if solution:  # a solution
        def value(out):  # a variable, a linear expression or a number, or lists of them
            if isinstance(out, (list, tuple)):
                return [value(item) for item in out]
            return out if isinstance(out, int) else round(out.solution_value)

        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution:", model.solve_details.status)

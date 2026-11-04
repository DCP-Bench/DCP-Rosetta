# csplib_011_acc_basketball_schedule: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from pychoco.model import Model

# Team numbers, in the order of the statement.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
# RIVALS[t] is the traditional rival of team t. FSU has no rival.
RIVALS = [GT, UNC, FSU, CLEM, UVA, DUKE, WAKE, UMD, NCST]
# MIRROR[d] is the date paired with date d in the mirroring scheme (Nemhauser and Trick):
# (1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18).
MIRROR = [7, 8, 11, 12, 13, 14, 15, 0, 1, 16, 17, 2, 3, 4, 5, 6, 9, 10]
# A team's status on a date.
HOME, BYE, AWAY = 0, 1, 2


def create_model(instance):
    """Schedule the 1997/98 Atlantic Coast Conference basketball season: each of the nine teams
    plays every other team once at home and once away over 18 dates, and the schedule follows
    the conference's rules on mirroring, home, away and bye patterns, weekends, rivals and
    opponent sequences."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates in the season
    teams = range(n_teams)
    days = range(n_days)
    # The second date and every other date after it is a weekend fixture.
    weekends = [d for d in days if d % 2 == 1]
    # The byes each team has: the dates left over after its 2 * (n_teams - 1) matches.
    n_byes = n_days - 2 * (n_teams - 1)

    model = Model()

    # config[d][i] is the team that team i plays on date d. config[d][i] == i is a bye.
    config = [[model.intvar(0, n_teams - 1, name=f"config_{d}_{i}") for i in teams] for d in days]
    # where[d][i] is HOME, BYE or AWAY for team i on date d.
    where = [[model.intvar(0, 2, name=f"where_{d}_{i}") for i in teams] for d in days]

    # is_home[d][i] is true when team i plays at home on date d. is_bye and is_away
    # are the same for a bye and for an away match.
    is_home = [[model.arithm(where[d][i], "=", HOME).reify() for i in teams] for d in days]
    is_bye = [[model.arithm(where[d][i], "=", BYE).reify() for i in teams] for d in days]
    is_away = [[model.arithm(where[d][i], "=", AWAY).reify() for i in teams] for d in days]
    # fixed[t] is team t as a fixed number, so that it can be looked up as an opponent.
    fixed = [model.intvar(t, t, name=f"team_{t}") for t in teams]

    for d in days:
        # No team is the opponent of two teams on one date.
        model.all_different(config[d]).post()
        for t in teams:
            # If team t plays team j, then team j plays team t.
            model.element(fixed[t], config[d], config[d][t]).post()
            # A bye is a match against oneself.
            model.arithm(config[d][t], "=", t).reify_with(is_bye[d][t])
            # Two teams that meet play one at home and one away. Their statuses add up to 2,
            # and a bye pairs a team with itself (1 + 1).
            opp_where = model.intvar(0, 2, name=f"opp_where_{d}_{t}")
            model.element(opp_where, where[d], config[d][t]).post()
            model.arithm(where[d][t], "+", opp_where, "=", 2).post()

    for t in teams:
        # slots[d] is the opponent and the status of team t on date d, as one number:
        # opponent + n_teams * status.
        slots = []
        for d in days:
            slot = model.intvar(0, 3 * n_teams - 1, name=f"slot_{d}_{t}")
            model.scalar([config[d][t], where[d][t]], [1, n_teams], "=", slot).post()
            slots.append(slot)
        # Team t plays every other team once at home and once away, and has n_byes byes.
        # values and occurrences give how often each number must appear in slots.
        values, occurrences = [], []
        for o in teams:
            if o != t:
                values += [o + n_teams * HOME, o + n_teams * AWAY]
                occurrences += [model.intvar(1, 1), model.intvar(1, 1)]
        values.append(t + n_teams * BYE)
        occurrences.append(model.intvar(n_byes, n_byes))
        model.global_cardinality(slots, values, occurrences, closed=True).post()

    # Counts that every season meets, which follow from the rules above.
    for t in teams:
        # Team t meets each other team on two dates and has n_byes byes.
        counts = [model.intvar(2, 2) if o != t else model.intvar(n_byes, n_byes) for o in teams]
        model.global_cardinality([config[d][t] for d in days], list(teams), counts).post()
        # Team t plays n_teams - 1 matches at home, n_teams - 1 away and has n_byes byes.
        model.sum([is_home[d][t] for d in days], "=", n_teams - 1).post()
        model.sum([is_away[d][t] for d in days], "=", n_teams - 1).post()
        model.sum([is_bye[d][t] for d in days], "=", n_byes).post()
    # On each date one team has a bye, and the other teams play in pairs, half at home and half away.
    for d in days:
        model.sum([is_bye[d][t] for t in teams], "=", 1).post()
        model.sum([is_home[d][t] for t in teams], "=", n_teams // 2).post()
        model.sum([is_away[d][t] for t in teams], "=", n_teams // 2).post()

    # 1. Mirroring: paired dates have the same opponents, with home and away swapped.
    for d in days:
        for t in teams:
            model.arithm(config[d][t], "=", config[MIRROR[d]][t]).post()
            model.arithm(where[d][t], "+", where[MIRROR[d]][t], "=", 2).post()

    # 2. No team plays away on both of the last two dates.
    for t in teams:
        model.sum([is_away[n_days - 2][t], is_away[n_days - 1][t]], "<=", 1).post()

    # 3. Home, away and bye runs.
    for t in teams:
        for d in range(n_days - 2):
            # No more than two home matches in a row.
            model.sum([is_home[d + k][t] for k in range(3)], "<=", 2).post()
            # No more than two away matches in a row.
            model.sum([is_away[d + k][t] for k in range(3)], "<=", 2).post()
        for d in range(n_days - 3):
            # No more than three away matches or byes in a row, so every four dates include a home match.
            model.sum([is_home[d + k][t] for k in range(4)], ">=", 1).post()
        for d in range(n_days - 4):
            # No more than four home matches or byes in a row, so every five dates include an away match.
            model.sum([is_away[d + k][t] for k in range(5)], ">=", 1).post()

    # 4. Weekend pattern: over the weekends, each team plays four matches at home, four away and has one bye.
    for t in teams:
        model.sum([is_home[d][t] for d in weekends], "=", 4).post()
        model.sum([is_away[d][t] for d in weekends], "=", 4).post()
        model.sum([is_bye[d][t] for d in weekends], "=", 1).post()

    # 5. First weekends: each team is at home or has a bye on at least two of the first five weekends.
    for t in teams:
        model.sum([is_home[d][t] for d in weekends[:5]] + [is_bye[d][t] for d in weekends[:5]],
                  ">=", 2).post()

    # 6. Rival matches: on the last date, each team except FSU plays its rival, plays FSU, or has a bye.
    for t in teams:
        if t != FSU:
            model.member(config[n_days - 1][t], sorted({RIVALS[t], FSU, t})).post()

    # 7. Constrained matches: each of Wake and GT meets both UNC and Duke at least once in dates 11 to 18.
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        # how many of the dates 11 to 18 bring a and b together, which is at least one
        meetings = model.intvar(1, n_days - 10, name=f"meet_{a}_{b}")
        model.count(b, [config[d][a] for d in range(10, n_days)], meetings).post()

    # 8. Opponent sequences. plays[o][d][t] is true when team t plays team o on date d.
    plays = {o: [[model.arithm(config[d][t], "=", o).reify() for t in teams] for d in days]
             for o in (UNC, DUKE, WAKE)}
    for t in teams:
        if t not in (DUKE, UNC):
            # No team plays away against UNC on one date and away against Duke on the next, in either order.
            for first, second in ((UNC, DUKE), (DUKE, UNC)):
                for d in range(n_days - 1):
                    model.sum([plays[first][d][t], is_away[d][t],
                               plays[second][d + 1][t], is_away[d + 1][t]], "<=", 3).post()
        if t not in (UNC, DUKE, WAKE):
            # No team plays UNC, Duke and Wake on three consecutive dates, in any order.
            # orders lists the six orders in which the three teams can come.
            orders = [(UNC, DUKE, WAKE), (UNC, WAKE, DUKE), (DUKE, UNC, WAKE),
                      (DUKE, WAKE, UNC), (WAKE, UNC, DUKE), (WAKE, DUKE, UNC)]
            for order in orders:
                for d in range(n_days - 2):
                    model.sum([plays[order[k]][d + k][t] for k in range(3)], "<=", 2).post()

    # 9. Fixed matches and byes from the statement. last is the last date.
    last = n_days - 1
    # UNC plays Duke on date 11 and on the last date.
    model.arithm(config[10][UNC], "=", DUKE).post()
    model.arithm(config[last][UNC], "=", DUKE).post()
    # UNC plays Clem on the second date.
    model.arithm(config[1][UNC], "=", CLEM).post()
    # Duke has a bye on date 16.
    model.arithm(where[15][DUKE], "=", BYE).post()
    # Wake does not play at home on date 17.
    model.arithm(where[16][WAKE], "!=", HOME).post()
    # Wake has a bye on the first date.
    model.arithm(where[0][WAKE], "=", BYE).post()
    # Clem, Duke, UMD and Wake do not play away on the last date.
    for t in (CLEM, DUKE, UMD, WAKE):
        model.arithm(where[last][t], "!=", AWAY).post()
    # Clem, FSU, GT and Wake do not play away on the first date.
    for t in (CLEM, FSU, GT, WAKE):
        model.arithm(where[0][t], "!=", AWAY).post()
    # FSU and NCSt do not have a bye on the last date.
    for t in (FSU, NCST):
        model.arithm(where[last][t], "!=", BYE).post()
    # UNC does not have a bye on the first date.
    model.arithm(where[0][UNC], "!=", BYE).post()

    return model, {"config": config, "where": where}, None


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs, objective = create_model(instances[index])
    solver = model.get_solver()

    if objective:  # optimisation: find a solution and prove no better one exists
        solution = solver.find_optimal_solution(**objective)
    else:  # satisfaction: any solution will do
        solution = solver.find_solution()

    if solution:
        solution_value = np.vectorize(solution.get_int_val)  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", solution_value(output))
    else:
        print("No solution")

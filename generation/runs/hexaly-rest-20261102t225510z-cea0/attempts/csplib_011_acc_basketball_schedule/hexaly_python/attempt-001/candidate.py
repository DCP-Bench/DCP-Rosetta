"""ACC basketball schedule: a double round-robin of 9 teams over 18 dates with mirroring, pattern and other constraints."""
import hexaly.optimizer as hx

# Teams in the order of the problem statement, numbered from 0
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
RIVALS = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
# The mirroring scheme (1-based dates) of Nemhauser and Trick, from the statement
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def build(instance):
    teams, days = instance["n_teams"], instance["n_days"]
    last = days - 1
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # game[d][i][j] = 1 if team i plays at home against team j on date d (0-based)
    game = [[[model.bool() if i != j else 0 for j in range(teams)] for i in range(teams)] for _ in range(days)]

    def plays(d, i, j):
        """1 if teams i and j meet on date d, at either ground."""
        return game[d][i][j] + game[d][j][i]

    home = [[model.sum([game[d][i][j] for j in range(teams) if j != i]) for i in range(teams)] for d in range(days)]
    away = [[model.sum([game[d][j][i] for j in range(teams) if j != i]) for i in range(teams)] for d in range(days)]
    bye = [[1 - home[d][i] - away[d][i] for i in range(teams)] for d in range(days)]

    # Double round-robin: every team plays every other team once at home and once away
    for i in range(teams):
        for j in range(teams):
            if i != j:
                model.constraint(model.sum([game[d][i][j] for d in range(days)]) == 1)
    # A team plays at most one game a date; with 9 teams, four games are played each date
    for d in range(days):
        for i in range(teams):
            model.constraint(home[d][i] + away[d][i] <= 1)

    # 1. Mirroring: the two dates of a pair have the same opponent for every team
    for first, second in MIRROR:
        for i in range(teams):
            for j in range(teams):
                if i != j:
                    model.constraint(plays(first - 1, i, j) == plays(second - 1, i, j))
    # 2. No team plays away on both last dates
    for i in range(teams):
        model.constraint(away[last - 1][i] + away[last][i] <= 1)
    # 3. Home/away/bye patterns
    for i in range(teams):
        for d in range(days - 2):
            model.constraint(model.sum([away[k][i] for k in range(d, d + 3)]) <= 2)  # at most 2 aways in a row
            model.constraint(model.sum([home[k][i] for k in range(d, d + 3)]) <= 2)  # at most 2 homes in a row
        for d in range(days - 3):
            model.constraint(model.sum([away[k][i] + bye[k][i] for k in range(d, d + 4)]) <= 3)  # 3 aways or byes
        for d in range(days - 4):
            model.constraint(model.sum([home[k][i] + bye[k][i] for k in range(d, d + 5)]) <= 4)  # 4 homes or byes
    # 4. Weekends (the even dates, 1-based): each team has four home, four away and one bye
    weekends = list(range(1, days, 2))
    for i in range(teams):
        model.constraint(model.sum([home[d][i] for d in weekends]) == 4)
        model.constraint(model.sum([away[d][i] for d in weekends]) == 4)
        model.constraint(model.sum([bye[d][i] for d in weekends]) == 1)
    # 5. Each team has a home match or a bye on at least two of the first five weekends
    for i in range(teams):
        model.constraint(model.sum([home[d][i] + bye[d][i] for d in weekends[:5]]) >= 2)
    # 6. On the last date every team but FSU plays its rival, unless it plays FSU or has a bye
    for i in range(teams):
        if i != FSU:
            model.constraint(plays(last, i, RIVALS[i]) + plays(last, i, FSU) + bye[last][i] >= 1)
    # 7. These pairings occur at least once in dates 11 to 18
    for a, b in ((WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)):
        model.constraint(model.sum([plays(d, a, b) for d in range(10, 18)]) >= 1)
    # 8. Opponent sequences
    for i in range(teams):
        for d in range(days - 1):
            # no two consecutive dates away against UNC and Duke
            if i not in (UNC, DUKE):
                model.constraint(game[d][UNC][i] + game[d + 1][DUKE][i] <= 1)
                model.constraint(game[d][DUKE][i] + game[d + 1][UNC][i] <= 1)
        for d in range(days - 2):
            # no three consecutive dates against UNC, Duke and Wake, each once
            met = [model.sum([plays(k, i, x) for k in range(d, d + 3)]) for x in (UNC, DUKE, WAKE)]
            model.constraint(model.or_(*[m == 0 for m in met]))
    # 9. Other constraints (dates 1-based in the statement)
    model.constraint(plays(last, UNC, DUKE) == 1)  # UNC plays its rival Duke on the last date
    model.constraint(plays(10, UNC, DUKE) == 1)  # and on date 11
    model.constraint(plays(1, UNC, CLEM) == 1)  # UNC plays Clem on date 2
    model.constraint(bye[15][DUKE] == 1)  # Duke has a bye on date 16
    model.constraint(home[16][WAKE] == 0)  # Wake does not play home on date 17
    model.constraint(bye[0][WAKE] == 1)  # Wake has a bye on date 1
    for i in (CLEM, DUKE, UMD, WAKE):
        model.constraint(away[last][i] == 0)  # these teams do not play away on the last date
    for i in (CLEM, FSU, GT, WAKE):
        model.constraint(away[0][i] == 0)  # these teams do not play away on the first date
    for i in (FSU, NCST):
        model.constraint(bye[last][i] == 0)  # neither has a bye on the last date
    model.constraint(bye[0][UNC] == 0)  # UNC does not have a bye on the first date

    # config[d][i] is the opponent of team i on date d (a team with a bye faces itself);
    # where[d][i] is 0 at home, 1 for a bye and 2 away
    config = [[model.sum([j * plays(d, i, j) for j in range(teams) if j != i]) + i * bye[d][i]
               for i in range(teams)] for d in range(days)]
    where = [[bye[d][i] + 2 * away[d][i] for i in range(teams)] for d in range(days)]
    return optimizer, {"config": config, "where": where}

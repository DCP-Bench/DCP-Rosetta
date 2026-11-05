"""Sports tournament scheduling: n teams, n - 1 weeks of n / 2 periods, every pair meeting once, each team
playing once a week and at most twice in any period."""
import hexaly.optimizer as hx


def build(instance):
    n = instance["n_teams"]  # the number of teams
    weeks, periods = n - 1, n // 2
    optimizer = hx.HexalyOptimizer()
    model = optimizer.model

    # game[w][p][i][j] = 1 if team i plays at home against team j in week w, period p
    game = [[[[model.bool() if i != j else 0 for j in range(n)] for i in range(n)]
             for _ in range(periods)] for _ in range(weeks)]

    def plays(w, p, team):
        """1 if the team plays in that slot, at home or away."""
        return model.sum(game[w][p][team][j] + game[w][p][j][team] for j in range(n) if j != team)

    # Every slot holds exactly one game
    for w in range(weeks):
        for p in range(periods):
            model.constraint(model.sum(game[w][p][i][j] for i in range(n) for j in range(n) if i != j) == 1)
    # Every team plays once a week
    for w in range(weeks):
        for team in range(n):
            model.constraint(model.sum(plays(w, p, team) for p in range(periods)) == 1)
    # Every team plays at most twice in the same period over the tournament
    for p in range(periods):
        for team in range(n):
            model.constraint(model.sum(plays(w, p, team) for w in range(weeks)) <= 2)
    # Every team plays every other team, once
    for i in range(n):
        for j in range(i + 1, n):
            model.constraint(model.sum(game[w][p][i][j] + game[w][p][j][i]
                                       for w in range(weeks) for p in range(periods)) == 1)

    # The home and away teams (numbered from 1) of each slot
    home = [[model.sum((i + 1) * game[w][p][i][j] for i in range(n) for j in range(n) if i != j)
             for p in range(periods)] for w in range(weeks)]
    away = [[model.sum((j + 1) * game[w][p][i][j] for i in range(n) for j in range(n) if i != j)
             for p in range(periods)] for w in range(weeks)]
    return optimizer, {"home": home, "away": away}

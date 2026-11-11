# csplib_026_sports_tournament_scheduling: a CPLEX (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install docplex cplex`; the CPLEX that comes
# with pip allows models up to 1000 variables and 1000 constraints):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from docplex.mp.model import Model


def create_model(instance):
    """Sports tournament scheduling: schedule a round robin of n teams over n-1 weeks, each week split
    into n/2 periods holding one game (a home team against an away team), so that every team plays
    once a week, at most twice in the same period over the tournament, and against every other team."""
    n_teams = instance["n_teams"]  # number of teams
    n_weeks, n_periods = n_teams - 1, n_teams // 2  # weeks, and games per week
    teams = range(1, n_teams + 1)
    slots = [(w, p) for w in range(n_weeks) for p in range(n_periods)]
    pairs = [(t1, t2) for t1 in teams for t2 in teams if t1 < t2]

    model = Model("sports_tournament_scheduling")

    # Every team plays every other team, and there are exactly as many game slots as pairs of
    # teams, so each pair meets exactly once. meet[g, s] = 1 when pair g plays in slot s. A
    # variable per pair and slot (784 at n = 8) is smaller than one per ordered pair and slot.
    meet = {(g, s): model.binary_var(name=f"meet_{g[0]}_{g[1]}_{s[0]}_{s[1]}") for g in pairs for s in slots}

    # Each pair of teams plays once.
    model.add_constraints(model.sum(meet[g, s] for s in slots) == 1 for g in pairs)

    # Each slot holds one game, between two different teams.
    model.add_constraints(model.sum(meet[g, s] for g in pairs) == 1 for s in slots)

    # Every team plays once a week.
    for w in range(n_weeks):
        for t in teams:
            model.add_constraint(model.sum(meet[g, (w, p)] for g in pairs if t in g
                                           for p in range(n_periods)) == 1)

    # Every team plays at most twice in the same period.
    for p in range(n_periods):
        for t in teams:
            model.add_constraint(model.sum(meet[g, (w, p)] for g in pairs if t in g
                                           for w in range(n_weeks)) <= 2)

    # The problem puts no rule on who plays at home, so in every game the team with the smaller
    # number is at home and the one with the larger number is away.
    # home[w][p] and away[w][p] are the home and away team of the game in week w, period p.
    home = [[model.sum(g[0] * meet[g, (w, p)] for g in pairs) for p in range(n_periods)]
            for w in range(n_weeks)]
    away = [[model.sum(g[1] * meet[g, (w, p)] for g in pairs) for p in range(n_periods)]
            for w in range(n_weeks)]

    return model, {"home": home, "away": away}


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

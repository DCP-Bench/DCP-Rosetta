# csplib_026_sports_tournament_scheduling: a Choco-solver (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install pychoco numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from pychoco.model import Model


def create_model(instance):
    """Schedule a tournament of n_teams teams over n_teams - 1 weeks, each week with n_teams / 2
    periods holding one match each. Every team plays once a week, every team plays every other
    team, and every team plays at most twice in the same period over the tournament."""
    n_teams = instance["n_teams"]  # the number of teams, numbered 1 to n_teams
    n_weeks = n_teams - 1          # every team meets each of the other teams once, one match a week
    n_periods = n_teams // 2       # the number of matches in a week, one in each period
    teams = list(range(1, n_teams + 1))

    model = Model()

    # pairs[m] is the m-th pair of teams, with the smaller team first
    pairs = [(t1, t2) for t1 in teams for t2 in teams if t1 < t2]
    # pair[w][p] is the index in pairs of the two teams that meet in period p of week w
    pair = [[model.intvar(0, len(pairs) - 1, name=f"pair_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]
    # home[w][p] is the home team of the match in period p of week w
    home = [[model.intvar(1, n_teams, name=f"home_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]
    # away[w][p] is the away team of the match in period p of week w
    away = [[model.intvar(1, n_teams, name=f"away_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]

    # A team does not play against itself.
    for w in range(n_weeks):
        for p in range(n_periods):
            model.arithm(home[w][p], "!=", away[w][p]).post()

    # Every team plays once a week.
    for w in range(n_weeks):
        model.all_different(home[w] + away[w]).post()

    # match_pair lists the ways a match can be set up: the home team, the away team and the index
    # of their pair, for each pair in both orders.
    match_pair = []
    for idx, (t1, t2) in enumerate(pairs):
        match_pair += [(t1, t2, idx), (t2, t1, idx)]
    # The home team, the away team and the pair index of each match agree.
    for w in range(n_weeks):
        for p in range(n_periods):
            model.table([home[w][p], away[w][p], pair[w][p]], match_pair).post()
    # There are as many matches as pairs of teams, and each pair meets once.
    model.all_different([pv for row in pair for pv in row]).post()

    # dummy[s] is the team in slot s of a dummy week. Slots 2p and 2p + 1 belong to period p.
    dummy = [model.intvar(1, n_teams, name=f"dummy_{s}") for s in range(n_teams)]
    # Every team is in the dummy week once.
    model.all_different(dummy).post()
    # A team plays n_teams - 1 matches in n_periods periods, at most twice in each, so it plays
    # in one period only once. The dummy week holds each team once, in that period, so every team
    # appears exactly twice in every period over the weeks and the dummy week.
    for p in range(n_periods):
        # The two dummy slots of a period hold two different teams, in increasing order.
        model.arithm(dummy[2 * p], "<", dummy[2 * p + 1]).post()
        # The appearances of the teams in period p, over the weeks and the dummy week.
        in_period = ([home[w][p] for w in range(n_weeks)] + [away[w][p] for w in range(n_weeks)]
                     + [dummy[2 * p], dummy[2 * p + 1]])
        # Each team appears exactly twice in period p.
        twice = [model.intvar(2, 2) for _ in teams]
        model.global_cardinality(in_period, teams, twice).post()

    return model, {"home": home, "away": away}, None


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

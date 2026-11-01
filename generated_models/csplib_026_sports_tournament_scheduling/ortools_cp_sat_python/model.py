# csplib_026_sports_tournament_scheduling: an OR-Tools CP-SAT (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install ortools`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from ortools.sat.python import cp_model


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks. Each week has n / 2 periods, and each
    period holds one match between a home team and an away team. Every team plays once a week,
    every team plays at most twice in the same period over the tournament, and every team plays
    every other team."""
    n_teams = instance["n_teams"]  # n: the number of teams, numbered 1 to n
    n_weeks = n_teams - 1         # every team meets each of the other n - 1 teams once
    n_periods = n_teams // 2      # the number of periods in a week, one match in each
    teams = range(1, n_teams + 1) # the team numbers, 1 to n

    model = cp_model.CpModel()

    # home[w][p] is the home team of the match in week w, period p
    home = [[model.new_int_var(1, n_teams, f"home_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]
    # away[w][p] is the away team of the match in week w, period p
    away = [[model.new_int_var(1, n_teams, f"away_{w}_{p}") for p in range(n_periods)]
            for w in range(n_weeks)]
    # is_home[w][p][t] is true when team t is the home team of the match in week w, period p
    is_home = [[{t: model.new_bool_var(f"is_home_{w}_{p}_{t}") for t in teams}
                for p in range(n_periods)] for w in range(n_weeks)]
    # is_away[w][p][t] is true when team t is the away team of the match in week w, period p
    is_away = [[{t: model.new_bool_var(f"is_away_{w}_{p}_{t}") for t in teams}
                for p in range(n_periods)] for w in range(n_weeks)]

    # Each match has one home team and one away team, and a team does not play itself.
    for w in range(n_weeks):
        for p in range(n_periods):
            model.add_exactly_one(is_home[w][p].values())
            model.add_exactly_one(is_away[w][p].values())
            model.add(home[w][p] == sum(t * is_home[w][p][t] for t in teams))
            model.add(away[w][p] == sum(t * is_away[w][p][t] for t in teams))
            model.add(home[w][p] != away[w][p])

    # Every team plays exactly once a week.
    for w in range(n_weeks):
        for t in teams:
            model.add(sum(is_home[w][p][t] + is_away[w][p][t] for p in range(n_periods)) == 1)

    # Every team meets every other team at least once, at home or away.
    for t1 in teams:
        for t2 in range(t1 + 1, n_teams + 1):
            # the ways teams t1 and t2 can meet, over all weeks and periods
            meetings = []
            for w in range(n_weeks):
                for p in range(n_periods):
                    for a, b in ((t1, t2), (t2, t1)):
                        # meet is true exactly when a is the home team and b the away team in this match
                        meet = model.new_bool_var(f"meet_{w}_{p}_{a}_{b}")
                        model.add_bool_and([is_home[w][p][a], is_away[w][p][b]]).only_enforce_if(meet)
                        model.add_bool_or([~is_home[w][p][a], ~is_away[w][p][b]]).only_enforce_if(~meet)
                        meetings.append(meet)
            model.add(sum(meetings) >= 1)

    # Every team plays at most twice in the same period over the tournament.
    for t in teams:
        for p in range(n_periods):
            model.add(sum(is_home[w][p][t] + is_away[w][p][t] for w in range(n_weeks)) <= 2)

    return model, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    solver = cp_model.CpSolver()
    solver_value = np.vectorize(solver.value)  # make it work on nested variables

    status = solver.solve(model)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for name, output in outputs.items():
            print(name, "=", solver_value(output))
    else:
        print("No solution:", solver.status_name(status))

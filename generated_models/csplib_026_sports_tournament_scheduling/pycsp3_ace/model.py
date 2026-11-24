# csplib_026_sports_tournament_scheduling: a PyCSP3 model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install pycsp3`, which also needs Java for its ACE solver):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from pycsp3 import *


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks, with each week divided into n / 2 periods, and
    each period divided into two slots. The first team in each slot plays at home, whilst the second plays
    the first team away. Every team plays once a week, every team plays at most twice in the same period
    over the tournament, and every team plays every other team. The teams are numbered from 1 to n."""
    n_teams = instance["n_teams"]     # the number of teams n
    n_weeks = n_teams - 1             # the tournament lasts n - 1 weeks
    n_periods = n_teams // 2          # each week has n / 2 periods (n is even)
    max_per_period = 2                # a team plays at most twice in the same period over the tournament
    code_base = n_teams + 1           # larger than any team number, so low * code_base + high is unique for each pair
    teams = range(1, n_teams + 1)

    # home[w][p] is the team playing at home in period p of week w
    home = VarArray(size=[n_weeks, n_periods], dom=teams)
    # away[w][p] is the team playing away in the same slot
    away = VarArray(size=[n_weeks, n_periods], dom=teams)
    # low[w][p] and high[w][p] are the smaller and the larger team of that match
    low = VarArray(size=[n_weeks, n_periods], dom=teams)
    high = VarArray(size=[n_weeks, n_periods], dom=teams)
    # pair[w][p] codes the two teams of that match as low * code_base + high; the largest code is below code_base * code_base
    pair = VarArray(size=[n_weeks, n_periods], dom=range(code_base * code_base))

    satisfy(
        # Every team plays once a week: the home and away teams of week w are all different.
        [AllDifferent(list(home[w]) + list(away[w])) for w in range(n_weeks)],
        # Every team plays at most twice in the same period over the tournament.
        [Cardinality(list(home[:, p]) + list(away[:, p]),
                     occurrences={team: range(max_per_period + 1) for team in teams})
         for p in range(n_periods)],
        # low and high are the smaller and larger team of each match.
        [Minimum([home[w][p], away[w][p]]) == low[w][p] for w in range(n_weeks) for p in range(n_periods)],
        [Maximum([home[w][p], away[w][p]]) == high[w][p] for w in range(n_weeks) for p in range(n_periods)],
        # Coding each match as low * code_base + high lets one AllDifferent say that no pair of teams meets twice
        # (the n(n - 1)/2 matches are all different, so every pair occurs exactly once).
        [pair[w][p] == low[w][p] * code_base + high[w][p] for w in range(n_weeks) for p in range(n_periods)],
        AllDifferent(pair[w][p] for w in range(n_weeks) for p in range(n_periods)),
    )

    return {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    outputs = create_model(instances[index])
    if solve() is SAT:
        print("home", "=")
        for row in outputs["home"]:
            print(values(row))
    else:
        print("No solution:", status())

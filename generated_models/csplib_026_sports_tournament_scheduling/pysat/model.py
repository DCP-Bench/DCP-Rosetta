# csplib_026_sports_tournament_scheduling: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Schedule a tournament of n teams over n - 1 weeks. Each week has n / 2 periods, and each
    period holds one match between a home team and an away team. Every team plays once a week,
    every team plays at most twice in the same period over the tournament, and every team plays
    every other team."""
    n_teams = instance["n_teams"]  # n, the number of teams, numbered from 1 to n
    n_weeks = n_teams - 1          # every team meets each of the other n - 1 teams once
    n_periods = n_teams // 2       # the number of periods in a week, each holding one match
    teams = range(1, n_teams + 1)  # the team numbers

    pool = IDPool()

    # home[w][p] is the home team of the match in week w, period p
    home = [[Integer(f"home_{w}_{p}", 1, n_teams, vpool=pool) for p in range(n_periods)]
            for w in range(n_weeks)]
    # away[w][p] is the away team of the match in week w, period p
    away = [[Integer(f"away_{w}_{p}", 1, n_teams, vpool=pool) for p in range(n_periods)]
            for w in range(n_weeks)]
    engine = IntegerEngine(vars=[t for week in home + away for t in week], vpool=pool)

    # Every team plays once a week: the home and away teams of a week are all different, so no team
    # plays itself either.
    for w in range(n_weeks):
        engine.add_alldifferent(home[w] + away[w])
    cnf = engine.clausify()

    # Every team plays every other team, in one of the matches.
    for t1, t2 in combinations(teams, 2):
        # the matches in which t1 and t2 meet, with either of them at home
        meetings = []
        for w in range(n_weeks):
            for p in range(n_periods):
                for a, b in ((t1, t2), (t2, t1)):
                    # meets is true when a is the home team and b the away team of this match
                    meets = pool.id(("meets", w, p, a, b))
                    cnf.append([-meets, home[w][p].equals(a)])
                    cnf.append([-meets, away[w][p].equals(b)])
                    meetings.append(meets)
        cnf.append(meetings)

    # Every team plays at most twice in the same period over the tournament.
    for p in range(n_periods):
        for t in teams:
            # plays[w] is true whenever team t takes part in the match of week w, period p
            plays = []
            for w in range(n_weeks):
                in_slot = pool.id(("plays", w, p, t))
                cnf.append([-home[w][p].equals(t), in_slot])
                cnf.append([-away[w][p].equals(t), in_slot])
                plays.append(in_slot)
            cnf.extend(CardEnc.atmost(lits=plays, bound=2, vpool=pool, encoding=EncType.seqcounter).clauses)

    return cnf, {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from pysat.solvers import Solver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    formula, outputs = create_model(instances[index])

    solver = Solver(bootstrap_with=formula)
    solver.solve()
    model = solver.get_model()  # None when there is no solution

    if model:
        value = np.vectorize(lambda var: var.decode(model))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

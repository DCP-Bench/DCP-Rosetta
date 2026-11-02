# csplib_026_sports_tournament_scheduling: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_026_sports_tournament_scheduling.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_026_sports_tournament_scheduling.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_026_sports_tournament_scheduling.py csplib_026_sports_tournament_scheduling.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, Or, add_to_container, to_cnf


def create_model(instance):
    """Schedule a round robin of n teams over n - 1 weeks, with n / 2 periods in each week and
    one game in each period between a home team and an away team. Every team plays once a
    week, at most twice in the same period over the tournament, and every two teams play
    each other exactly once."""
    n = instance["n_teams"]  # the number of teams
    weeks = n - 1            # every team plays once a week, against each other team once
    periods = n // 2         # the games of one week
    teams = range(n)         # the teams, numbered 0 to n - 1 here

    # is_home[w][p][t] is true when team t is the home team of the game in week w, period p
    is_home = [[[Bool(f"home_{w}_{p}_{t}") for t in teams] for p in range(periods)]
               for w in range(weeks)]
    # is_away[w][p][t] is true when team t is the away team of that game
    is_away = [[[Bool(f"away_{w}_{p}_{t}") for t in teams] for p in range(periods)]
               for w in range(weeks)]

    constraints = []

    # Each game has one home team and one away team.
    for w in range(weeks):
        for p in range(periods):
            constraints.append(sum(is_home[w][p]) == 1)
            constraints.append(sum(is_away[w][p]) == 1)

    # Every team plays once a week, as home or as away.
    for w in range(weeks):
        for t in teams:
            constraints.append(sum(is_home[w][p][t] + is_away[w][p][t] for p in range(periods)) == 1)

    # Every team plays at most twice in the same period over the tournament.
    for p in range(periods):
        for t in teams:
            constraints.append(sum(is_home[w][p][t] + is_away[w][p][t] for w in range(weeks)) <= 2)

    # meet[w, p, i, j] is true when teams i and j play each other in period p of week w, in either order.
    meet = {}
    for w in range(weeks):
        for p in range(periods):
            for i in teams:
                for j in teams:
                    if i < j:
                        meet[w, p, i, j] = Bool(f"meet_{w}_{p}_{i}_{j}")
                        constraints.append(Iff(meet[w, p, i, j], Or([is_home[w][p][i] & is_away[w][p][j],
                                                                     is_home[w][p][j] & is_away[w][p][i]])))

    # Every two teams play each other exactly once over the tournament.
    for i in teams:
        for j in teams:
            if i < j:
                constraints.append(sum(meet[w, p, i, j] for w in range(weeks) for p in range(periods)) == 1)

    # The home and away team of each game, numbered 1 to n.
    home = [[sum((t + 1) * is_home[w][p][t] for t in teams) for p in range(periods)] for w in range(weeks)]
    away = [[sum((t + 1) * is_away[w][p][t] for t in teams) for p in range(periods)] for w in range(weeks)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"home": home, "away": away}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

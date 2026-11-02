# csplib_011_acc_basketball_schedule: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_011_acc_basketball_schedule.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_011_acc_basketball_schedule.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_011_acc_basketball_schedule.py csplib_011_acc_basketball_schedule.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Or, add_to_container, to_cnf

# Teams, numbered as the problem lists them: Clemson, Duke, Florida State, Georgia Tech,
# Maryland, North Carolina, NC State, Virginia, Wake Forest.
CLEM, DUKE, FSU, GT, UMD, UNC, NCST, UVA, WAKE = range(9)
# Traditional rivals: Duke and UNC, Clemson and Georgia Tech, NC State and Wake Forest,
# Maryland and Virginia. FSU has none.
RIVAL = {DUKE: UNC, UNC: DUKE, CLEM: GT, GT: CLEM, NCST: WAKE, WAKE: NCST, UMD: UVA, UVA: UMD}
# Pairs of dates that mirror each other: each team meets the same opponent on both dates of a pair.
MIRROR = [(1, 8), (2, 9), (3, 12), (4, 13), (5, 14), (6, 15), (7, 16), (10, 17), (11, 18)]


def create_model(instance):
    """Schedule a double round-robin for the teams of the 1997/98 Atlantic Coast Conference
    basketball tournament over the given number of dates. Each team plays every other team
    once at home and once away, and has a bye on the dates it does not play. The schedule
    must follow the conference's rules. Give config, the opponent of each team on each date,
    and where, the venue of each team on each date."""
    n_teams = instance["n_teams"]  # the number of teams
    n_days = instance["n_days"]    # the number of dates

    teams = range(n_teams)
    dates = range(1, n_days + 1)
    weekends = [d for d in dates if d % 2 == 0]  # even dates are weekend fixtures
    first_weekends = weekends[:5]                # the first five weekends
    last_date = n_days
    penultimate_date = n_days - 1

    # home[d, i, j] is true when team i plays at home against team j on date d.
    home = {(d, i, j): Bool(f"home_{d}_{i}_{j}") for d in dates for i in teams for j in teams if i != j}
    # bye[d, i] is true when team i has a bye on date d.
    bye = {(d, i): Bool(f"bye_{d}_{i}") for d in dates for i in teams}

    # Team i plays at home on date d.
    def H(d, i):
        return sum(home[d, i, j] for j in teams if j != i)

    # Team i plays away on date d.
    def A(d, i):
        return sum(home[d, j, i] for j in teams if j != i)

    # Teams i and j meet on date d, at either venue.
    def M(d, i, j):
        return home[d, i, j] | home[d, j, i]

    constraints = []

    # On each date a team plays one match or has a bye.
    for d in dates:
        for i in teams:
            constraints.append(H(d, i) + A(d, i) + bye[d, i] == 1)

    # Each team plays each other team once at home.
    for i in teams:
        for j in teams:
            if i != j:
                constraints.append(sum(home[d, i, j] for d in dates) == 1)

    # The two dates of a mirror pair have the same opponents.
    for r1, r2 in MIRROR:
        for i in teams:
            for j in teams:
                if i != j:
                    constraints.append(M(r1, i, j) == M(r2, i, j))

    # No team plays away on both of the last two dates.
    for i in teams:
        constraints.append(A(penultimate_date, i) + A(last_date, i) <= 1)

    # No team has more than two away matches in a row.
    for i in teams:
        for d in range(1, n_days - 1):
            constraints.append(sum(A(d + k, i) for k in range(3)) <= 2)

    # No team has more than two home matches in a row.
    for i in teams:
        for d in range(1, n_days - 1):
            constraints.append(sum(H(d + k, i) for k in range(3)) <= 2)

    # No team has more than three away matches or byes in a row.
    for i in teams:
        for d in range(1, n_days - 2):
            constraints.append(sum(A(d + k, i) + bye[d + k, i] for k in range(4)) <= 3)

    # No team has more than four home matches or byes in a row.
    for i in teams:
        for d in range(1, n_days - 3):
            constraints.append(sum(H(d + k, i) + bye[d + k, i] for k in range(5)) <= 4)

    # Over the weekends each team plays four matches at home, four away and has one bye.
    for i in teams:
        constraints.append(sum(H(d, i) for d in weekends) == 4)
        constraints.append(sum(A(d, i) for d in weekends) == 4)
        constraints.append(sum(bye[d, i] for d in weekends) == 1)

    # Each team has a home match or a bye on at least two of the first five weekends.
    for i in teams:
        constraints.append(sum(H(d, i) + bye[d, i] for d in first_weekends) >= 2)

    # On the last date each team with a rival plays that rival, unless it plays FSU or has a bye.
    for i in teams:
        if i in RIVAL:
            constraints.append(Or([M(last_date, i, RIVAL[i]), M(last_date, i, FSU), bye[last_date, i]]))

    # Wake Forest and Georgia Tech each meet UNC and Duke at least once from date 11 on.
    for i, j in [(WAKE, UNC), (WAKE, DUKE), (GT, UNC), (GT, DUKE)]:
        constraints.append(Or([M(d, i, j) for d in dates if d >= 11]))

    # No team plays away at UNC and away at Duke on two consecutive dates, in either order.
    for i in teams:
        for d in range(1, n_days):
            for x, y in [(UNC, DUKE), (DUKE, UNC)]:
                if i not in (x, y):
                    constraints.append(~(home[d, x, i] & home[d + 1, y, i]))

    # The three teams UNC, Duke and Wake, in each of their six orders.
    trio = [UNC, DUKE, WAKE]
    orders = [(a, b, c) for a in trio for b in trio for c in trio if len({a, b, c}) == 3]
    # No team meets UNC, Duke and Wake on three consecutive dates, at either venue.
    for i in teams:
        if i in trio:
            continue
        for d in range(1, n_days - 1):
            for a, b, c in orders:
                constraints.append(~(M(d, i, a) & M(d + 1, i, b) & M(d + 2, i, c)))

    # UNC plays Duke on the last date and on date 11.
    constraints.append(M(last_date, UNC, DUKE))
    constraints.append(M(11, UNC, DUKE))
    # UNC plays Clemson on the second date.
    constraints.append(M(2, UNC, CLEM))
    # Duke has a bye on date 16.
    constraints.append(bye[16, DUKE])
    # Wake Forest does not play at home on date 17.
    constraints.append(H(17, WAKE) == 0)
    # Wake Forest has a bye on the first date.
    constraints.append(bye[1, WAKE])
    # Clemson, Duke, UMD and Wake Forest do not play away on the last date.
    for i in [CLEM, DUKE, UMD, WAKE]:
        constraints.append(A(last_date, i) == 0)
    # Clemson, FSU, Georgia Tech and Wake Forest do not play away on the first date.
    for i in [CLEM, FSU, GT, WAKE]:
        constraints.append(A(1, i) == 0)
    # Neither FSU nor NC State has a bye on the last date.
    constraints.append(~bye[last_date, FSU])
    constraints.append(~bye[last_date, NCST])
    # UNC does not have a bye on the first date.
    constraints.append(~bye[1, UNC])

    # Opponent of each team on each date; a team with a bye stands in for itself.
    config = [
        [
            sum(j * home[d, i, j] + j * home[d, j, i] for j in teams if j != i) + i * bye[d, i]
            for i in teams
        ]
        for d in dates
    ]
    # Venue of each team on each date: 0 home, 1 bye, 2 away.
    where = [
        [sum(2 * home[d, j, i] for j in teams if j != i) + 1 * bye[d, i] for i in teams]
        for d in dates
    ]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"config": config, "where": where}


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

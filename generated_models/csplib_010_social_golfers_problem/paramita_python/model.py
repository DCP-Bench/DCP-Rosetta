# csplib_010_social_golfers_problem: a Paramita (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no golfer plays in the same group as any other golfer on more than one occasion. Give
    assign[i][j], the group of golfer i in week j, counted from 0."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in a group
    n_golfers = n_groups * group_size    # every group is full, so this many golfers play each week

    # p[i][j][g] is true when golfer i plays in group g in week j.
    p = [[[Bool(f"p_{i}_{j}_{g}") for g in range(n_groups)]
          for j in range(n_weeks)] for i in range(n_golfers)]

    constraints = []

    # Each golfer plays in exactly one group each week.
    for i in range(n_golfers):
        for j in range(n_weeks):
            constraints.append(sum(p[i][j]) == 1)

    # Each group holds exactly group_size golfers in each week.
    for j in range(n_weeks):
        for g in range(n_groups):
            constraints.append(sum(p[i][j][g] for i in range(n_golfers)) == group_size)

    # The golfers are interchangeable, so fix week 0: the first group_size golfers form
    # group 0, the next group_size form group 1, and so on.
    for i in range(n_golfers):
        constraints.append(p[i][0][i // group_size])

    # meet[a, b, j] is true when golfers a and b play in the same group in week j. Both
    # orders of a pair share one flag.
    meet = {}
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            for j in range(n_weeks):
                m = Bool(f"meet_{a}_{b}_{j}")
                meet[a, b, j] = m
                meet[b, a, j] = m
                # Two golfers meet in week j exactly when they play in the same group that week.
                for g in range(n_groups):
                    constraints.append(~p[a][j][g] | ~p[b][j][g] | m)
                    constraints.append(~m | ~p[a][j][g] | p[b][j][g])

    # Two golfers meet in at most one week.
    for a in range(n_golfers):
        for b in range(a + 1, n_golfers):
            constraints.append(sum(meet[a, b, j] for j in range(n_weeks)) <= 1)

    # Each golfer meets the other group_size - 1 members of their group in each week.
    for a in range(n_golfers):
        for j in range(n_weeks):
            constraints.append(sum(meet[a, b, j] for b in range(n_golfers) if b != a)
                               == group_size - 1)

    # Group of each golfer in each week.
    assign = [[sum(g * p[i][j][g] for g in range(n_groups)) for j in range(n_weeks)]
              for i in range(n_golfers)]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"assign": assign}


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

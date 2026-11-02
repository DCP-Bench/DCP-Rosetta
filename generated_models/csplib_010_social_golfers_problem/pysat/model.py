# csplib_010_social_golfers_problem: a PySAT (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install "python-sat[pblib]" numpy`):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def create_model(instance):
    """Golfers play once a week, always in groups of the same size. Schedule the play so that
    no two golfers are in the same group on more than one occasion."""
    n_weeks = instance["n_weeks"]        # the number of weeks of play
    n_groups = instance["n_groups"]      # the number of groups playing each week
    group_size = instance["group_size"]  # the number of golfers in each group
    n_golfers = n_groups * group_size    # every golfer plays every week, so the golfers fill all groups

    pool = IDPool()

    # assign[g][w]: the group, counted from 0, that golfer g plays in during week w
    assign = [[Integer(f"assign{g}_{w}", 0, n_groups - 1, vpool=pool) for w in range(n_weeks)]
              for g in range(n_golfers)]
    engine = IntegerEngine(vars=[a for row in assign for a in row], vpool=pool)
    cnf = engine.clausify()

    # in_group[g][w][k]: golfer g is in group k in week w
    in_group = [[[assign[g][w].equals(k) for k in range(n_groups)] for w in range(n_weeks)]
                for g in range(n_golfers)]

    # Each group has exactly group_size golfers in every week.
    for w in range(n_weeks):
        for k in range(n_groups):
            cnf.extend(CardEnc.equals(lits=[in_group[g][w][k] for g in range(n_golfers)],
                                      bound=group_size, vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    # Two golfers share a group in at most one week. meet[w] is set whenever both golfers are
    # in the same group in week w, and at most one week may have it set.
    for g1, g2 in combinations(range(n_golfers), 2):
        meet = []
        for w in range(n_weeks):
            flag = pool.id(("meet", g1, g2, w))
            for k in range(n_groups):
                cnf.append([-in_group[g1][w][k], -in_group[g2][w][k], flag])
            meet.append(flag)
        cnf.extend(CardEnc.atmost(lits=meet, bound=1, vpool=pool,
                                  encoding=EncType.pairwise).clauses)

    return cnf, {"assign": assign}


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

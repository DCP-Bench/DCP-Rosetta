# csplib_010_social_golfers_problem: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_010_social_golfers_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_010_social_golfers_problem.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_010_social_golfers_problem.py csplib_010_social_golfers_problem.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """A club schedules its golfers into groups of a fixed size each week, for a number of
    weeks, so that no two golfers play in the same group on more than one occasion."""
    group_size = instance["group_size"]  # the number of golfers in each group
    n_groups = instance["n_groups"]      # the number of groups that play each week
    n_weeks = instance["n_weeks"]        # the number of weeks of play

    golfers = range(n_groups * group_size)  # golfer numbers 0 .. n_groups * group_size - 1
    weeks = range(n_weeks)                  # week numbers 0 .. n_weeks - 1
    groups = range(n_groups)                # group numbers 0 .. n_groups - 1 (0-indexed, as the output requires)
    # every pair of golfers i < k, for the no-repeat rule
    pairs = [(i, k) for i in golfers for k in golfers if i < k]

    model = gp.Model("social_golfers")

    # plays[i, j, g] is 1 when golfer i plays in group g in week j, and 0 when not
    plays = model.addVars(golfers, weeks, groups, vtype=GRB.BINARY, name="plays")

    # group_of[i, j] is the group number of golfer i in week j; it is the number of the one group
    # that golfer plays in (the range 0 .. n_groups - 1 is the group numbering of the output)
    group_of = model.addVars(golfers, weeks, lb=0, ub=n_groups - 1, vtype=GRB.INTEGER, name="group_of")

    # together[i, k, j] is 1 when golfers i and k are both in the same group in week j
    together = model.addVars(pairs, weeks, vtype=GRB.BINARY, name="together")

    # Each golfer plays in exactly one group each week.
    model.addConstrs((gp.quicksum(plays[i, j, g] for g in groups) == 1
                      for i in golfers for j in weeks), name="one_group")

    # group_of reads back the group that each golfer plays in.
    model.addConstrs((group_of[i, j] == gp.quicksum(g * plays[i, j, g] for g in groups)
                      for i in golfers for j in weeks), name="group_number")

    # Each group has exactly group_size golfers in each week.
    model.addConstrs((gp.quicksum(plays[i, j, g] for i in golfers) == group_size
                      for j in weeks for g in groups), name="group_size")

    # If golfers i and k share a group in week j, their together variable is forced to 1.
    model.addConstrs((together[i, k, j] >= plays[i, j, g] + plays[k, j, g] - 1
                      for (i, k) in pairs for j in weeks for g in groups), name="together_link")

    # Two golfers share a group in at most one week.
    model.addConstrs((together.sum(i, k, "*") <= 1 for (i, k) in pairs), name="meet_once")

    # Symmetry breaking (not in the statement): groups and golfers are interchangeable, so week 0
    # can be fixed to the groups in order, golfer i in group i // group_size.
    model.addConstrs((plays[i, 0, i // group_size] == 1 for i in golfers), name="week0_fixed")

    # There is no objective: any schedule meeting the rules is an answer.
    return model, {"assign": [[group_of[i, j] for j in weeks] for i in golfers]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded

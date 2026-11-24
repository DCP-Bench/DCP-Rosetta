# csplib_013_progressive_party_problem: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_013_progressive_party_problem.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_013_progressive_party_problem.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_013_progressive_party_problem.py csplib_013_progressive_party_problem.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Progressive party: some boats are hosts, and the crews of the other boats visit the hosts over
    several periods, never exceeding a boat's capacity and never meeting another crew twice.
    Use as few host boats as possible."""
    n_boats = instance["n_boats"]      # how many boats there are, numbered 0 to n_boats - 1
    n_periods = instance["n_periods"]  # how many half-hour periods the party lasts
    capacity = instance["capacity"]    # capacity[b] is the most people boat b can hold
    crew_size = instance["crew_size"]  # crew_size[b] is how many people are in boat b's crew
    boats = range(n_boats)
    periods = range(n_periods)

    model = gp.Model("progressive_party")

    # is_host[b] is 1 when boat b is a host boat, and 0 when it is a guest boat.
    is_host = model.addVars(boats, vtype=GRB.BINARY, name="is_host")

    # at[p, c, h] is 1 when the crew of boat c is on boat h in period p, and 0 when not. A host's
    # crew stays on its own boat. This is the visit schedule: visits[p][c] is the boat h where at[p, c, h] is 1.
    at = model.addVars(periods, boats, boats, vtype=GRB.BINARY, name="at")

    # Each crew is on exactly one boat in each period (at.sum(p, c, "*") adds over the boats h).
    model.addConstrs((at.sum(p, c, "*") == 1 for p in periods for c in boats), name="one_boat")

    # visits[p][c] is the boat that crew c visits, that is, is on, in period p.
    visits = [[gp.quicksum(h * at[p, c, h] for h in boats) for c in boats] for p in periods]

    # The crew of a host boat stays on its own boat in every period.
    model.addConstrs((at[p, b, b] >= is_host[b] for p in periods for b in boats), name="host_stays")

    # A boat that is not a host is never visited. at.sum(p, "*", h) counts the crews on boat h in
    # period p (the "*" adds over the crews). n_boats is a big-M: no more than n_boats crews
    # can be on a boat, so the bound is inactive when h is a host.
    model.addConstrs((at.sum(p, "*", h) <= n_boats * is_host[h] for p in periods for h in boats),
                     name="only_hosts")

    # The people on a boat, its host crew and the guest crews together, never exceed its capacity.
    model.addConstrs((gp.quicksum(crew_size[c] * at[p, c, h] for c in boats) <= capacity[h]
                      for p in periods for h in boats), name="capacity")

    # A guest crew never revisits a host: at.sum("*", c, h) counts the periods in which crew c is on
    # boat h (the "*" adds over the periods). A host crew is on its own boat in every period, so for a
    # host c the bound is relaxed to n_periods, and the bound 1 + (n_periods - 1) * is_host[c] allows that.
    model.addConstrs((at.sum("*", c, h) <= 1 + (n_periods - 1) * is_host[c]
                      for c in boats for h in boats), name="once")

    # Two crews meet in a period when they are on the same boat. same[p, a, b] is 1 when crews a and b
    # are on the same boat in period p. higher[p, a, b] records which way their boats differ when they
    # are not on the same boat. n_boats is a big-M, larger than any difference between two boat numbers,
    # so the constraints that do not apply in a case are switched off.
    for a in boats:
        for b in range(a + 1, n_boats):
            met = []
            for p in periods:
                same = model.addVar(vtype=GRB.BINARY, name=f"same[{p},{a},{b}]")
                higher = model.addVar(vtype=GRB.BINARY, name=f"higher[{p},{a},{b}]")
                model.addConstr(visits[p][a] - visits[p][b] + n_boats * same - n_boats * higher
                                >= 1 - n_boats, name=f"apart_up[{p},{a},{b}]")
                model.addConstr(visits[p][b] - visits[p][a] + n_boats * same + n_boats * higher >= 1,
                                name=f"apart_down[{p},{a},{b}]")
                met.append(same)
            # Crews a and b meet in at most one period.
            model.addConstr(gp.quicksum(met) <= 1, name=f"meet_once[{a},{b}]")

    # Minimise the number of host boats (is_host.sum() adds over all boats).
    model.setObjective(is_host.sum(), GRB.MINIMIZE)

    # is_host is printed as a list of 0/1 values, one per boat.
    return model, {"visits": visits, "is_host": [is_host[b] for b in boats]}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    model, outputs = create_model(instances[index])
    model.Params.OutputFlag = 0  # no solver log
    model.Params.MIPGap = 0  # prove the optimum; the default stops within 0.01% of it
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a proven optimum
        print("Objective value:", round(model.ObjVal))
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded

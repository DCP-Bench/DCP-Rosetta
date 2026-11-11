# csplib_018_water_bucket: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_018_water_bucket.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_018_water_bucket.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_018_water_bucket.py csplib_018_water_bucket.json

import itertools

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Water bucket: pour water between three buckets, of 8, 5 and 3 pints, to leave 4 pints in the 8 pint bucket and 4 in the 5 pint bucket, in as few transfers as possible."""
    capacities = instance["capacities"]  # capacities[b]: the pints bucket b holds (8, 5 and 3 in the statement)
    initial_state = tuple(instance["initial_state"])  # the pints in each bucket at the start ([8, 0, 0] in the statement)
    goal_state = tuple(instance["goal_state"])  # the pints in each bucket at the goal ([4, 4, 0] in the statement)
    steps = instance["MAX_STEPS"]  # the number of states the output sequence must list
    pad = instance["PADDING_VALUE"]  # the value printed for each bucket on the padding steps after the goal
    buckets = range(len(capacities))

    # The total water never changes: all of it is poured between the buckets.
    total_water = sum(initial_state)
    # The states are the ways to share the total water among the buckets, each bucket within its capacity.
    states = [s for s in itertools.product(*(range(c + 1) for c in capacities))
              if sum(s) == total_water]

    # Pouring from one bucket into another moves water until the first is empty or the second is full, and moves some water.
    def successors(state):
        result = set()
        for i in buckets:
            for j in buckets:
                if i == j:
                    continue
                amount = min(state[i], capacities[j] - state[j])
                if amount > 0:
                    nxt = list(state)
                    nxt[i] -= amount
                    nxt[j] += amount
                    result.add(tuple(nxt))
        return result

    # predecessors[s]: the states from which one transfer reaches s.
    predecessors = {s: [] for s in states}
    for s in states:
        for nxt in successors(s):
            if nxt in predecessors:
                predecessors[nxt].append(s)

    model = gp.Model("water_bucket")

    # at[t, k] is 1 when step t of the sequence is in state k of states. The index k = len(states), the one after the last state, is the padding step.
    padding = len(states)
    at = model.addVars(steps, range(len(states) + 1), vtype=GRB.BINARY, name="at")
    index = {s: k for k, s in enumerate(states)}  # index[s]: the position of state s in states
    start = index[initial_state]  # the position of the initial state in states
    goal = index[goal_state]  # the position of the goal state in states

    # Every step is in exactly one state, real or padding.
    model.addConstrs((at.sum(t, "*") == 1 for t in range(steps)), name="one_state")

    # The sequence starts with the initial state.
    model.addConstr(at[0, start] == 1, name="start")

    # Once padding has begun, it stays on: the step after a padding step is padding.
    model.addConstrs((at[t + 1, padding] >= at[t, padding] for t in range(steps - 1)), name="stay_padded")
    # Once the goal is reached, the sequence stops: the step after the goal is padding.
    model.addConstrs((at[t + 1, padding] >= at[t, goal] for t in range(steps - 1)), name="pad_after_goal")
    # Padding starts only after the goal: a step is padding only if the step before was padding or the goal.
    model.addConstrs((at[t + 1, padding] <= at[t, padding] + at[t, goal]
                      for t in range(steps - 1)), name="pad_only_after_goal")
    # Otherwise the next state follows from the current one by a single transfer: a state can be entered only from one of its predecessors.
    sources = [[index[p] for p in predecessors[s]] for s in states]
    model.addConstrs((at[t + 1, k] <= gp.quicksum(at[t, j] for j in sources[k])
                      for t in range(steps - 1) for k in range(len(states))), name="transfer")

    # The goal state is reached at some step.
    model.addConstr(at.sum("*", goal) >= 1, name="reach_goal")

    # The amount in each bucket at each step, or the padding value on the padding steps.
    sequence = [[gp.quicksum(states[k][b] * at[t, k] for k in range(len(states))) + pad * at[t, padding]
                 for b in buckets] for t in range(steps)]

    # Objective: the number of transfers, which is the number of steps before padding minus one, since the starting state is not a transfer.
    cost = gp.quicksum(1 - at[t, padding] for t in range(steps)) - 1
    model.setObjective(cost, GRB.MINIMIZE)

    return model, {"cost": cost, "sequence": sequence}


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

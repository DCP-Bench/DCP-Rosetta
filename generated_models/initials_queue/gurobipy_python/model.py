# initials_queue: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/initials_queue.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python initials_queue.py

import itertools

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. Letters A..E are 0..4; the queue length
# and the three known positions come from the statement.
N = 10                                        # the first 10 people in the queue (from the statement)
LETTERS = range(5)                            # the letters A to E, numbered 0 to 4
A, B, C, D, E = LETTERS
KNOWN = {0: (B, E), 1: (C, D), N - 1: (B, D)}  # BE at the front, CD right behind, BD at the end (from the statement)


def create_model(instance):
    """Initials queue: order ten people, whose initials are distinct ordered pairs of A-E, so that neighbours share no letter."""
    model = gp.Model("initials_queue")

    # The possible initials: two distinct letters, in alphabetical order.
    pairs = list(itertools.combinations(LETTERS, 2))

    # has[i, p] is 1 when the person at place i of the queue has the initials pairs[p], and 0 when not.
    has = model.addVars(N, len(pairs), vtype=GRB.BINARY, name="has")

    # Each person has exactly one pair of initials.
    model.addConstrs((has.sum(i, "*") == 1 for i in range(N)), name="one_pair")

    # No two people have the same initials.
    model.addConstrs((has.sum("*", p) <= 1 for p in range(len(pairs))), name="distinct")

    # uses(i, letter) is 1 when the person at place i has the letter in their initials.
    def uses(i, letter):
        return gp.quicksum(has[i, p] for p, pair in enumerate(pairs) if letter in pair)

    # No one shares a letter with the person in front: for each letter, at most one of two neighbours has it.
    model.addConstrs((uses(i, letter) + uses(i + 1, letter) <= 1
                      for i in range(N - 1) for letter in LETTERS), name="no_shared")

    # The known places: BE at the front, CD right behind, BD at the end.
    model.addConstrs((has[i, pairs.index(pair)] == 1 for i, pair in KNOWN.items()), name="known")

    # queue[i][k] is the k-th letter (0 for the first, 1 for the second) of the initials of the
    # person at place i, numbered 0 for A to 4 for E.
    queue = [[gp.quicksum(pair[k] * has[i, p] for p, pair in enumerate(pairs)) for k in range(2)]
             for i in range(N)]
    return model, {"queue": queue}


if __name__ == "__main__":
    import numpy as np

    model, outputs = create_model({})
    model.Params.OutputFlag = 0  # no solver log
    model.optimize()

    if model.Status == GRB.OPTIMAL:  # a solution
        # a variable's value is var.X, an expression's is expr.getValue(); both read through LinExpr
        value = np.vectorize(lambda out: round(gp.LinExpr(out).getValue()))
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution, Gurobi status", model.Status)  # 3 infeasible, 4 infeasible or unbounded

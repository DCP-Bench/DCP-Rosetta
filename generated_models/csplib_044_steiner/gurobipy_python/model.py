# csplib_044_steiner: a Gurobi (Python) model from DCP Rosetta.
# Download the `csplib_044_steiner.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_044_steiner.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python csplib_044_steiner.py csplib_044_steiner.json

import itertools

import gurobipy as gp
from gurobipy import GRB

# A triple is a set of three distinct elements; two elements together are in at most one triple.
TRIPLE_SIZE = 3  # every block of the system has three elements
PAIR_SIZE = 2    # the pairs of elements that must not repeat across blocks


def create_model(instance):
    """Find n*(n-1)/6 triples of distinct elements from 1 to n such that any two triples
    share at most one element (a ternary Steiner system of order n, which needs n mod 6
    to be 1 or 3)."""
    n = instance["n"]  # the number of elements; here they are numbered 0 to n-1

    elements = range(n)                                  # the elements (the statement's 1 to n, shifted to 0-based)
    num_triples = n * (n - 1) // 6                       # the statement asks for n(n-1)/6 triples, one per output row
    rows = range(num_triples)                            # the output rows
    candidates = list(itertools.combinations(elements, TRIPLE_SIZE))  # every possible triple of distinct elements

    model = gp.Model("steiner")

    # pick[i, k] is 1 when row i is the k-th candidate triple, and 0 when not
    pick = model.addVars(num_triples, len(candidates), vtype=GRB.BINARY, name="pick")

    # member[i, j] is 1 when element j is in the triple of row i, and 0 when not (the output)
    member = model.addVars(num_triples, n, vtype=GRB.BINARY, name="member")

    # Each row is exactly one candidate triple (pick.sum(i, "*") adds pick[i, k] over all candidates k).
    model.addConstrs((pick.sum(i, "*") == 1 for i in rows), name="one_triple")

    # member[i, j] agrees with the chosen triple of row i.
    model.addConstrs((member[i, j] == gp.quicksum(pick[i, k] for k, T in enumerate(candidates) if j in T)
                      for i in rows for j in elements), name="link")

    # Any two triples share at most one element: each pair of elements lies in at most one row's triple
    # (summed over all rows and all candidate triples that contain the pair).
    model.addConstrs((gp.quicksum(pick[i, k] for i in rows for k, T in enumerate(candidates)
                                  if e in T and f in T) <= 1
                      for e, f in itertools.combinations(elements, PAIR_SIZE)), name="pair_once")

    # No objective is set: any valid system is a solution, so this is a satisfaction problem.

    # sets[i][j] is true when element j is in the triple of row i
    return model, {"sets": [[member[i, j] for j in elements] for i in rows]}


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

# session2_subsets_100: a Gurobi (Python) model from DCP Rosetta.
# Download the `session2_subsets_100.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session2_subsets_100.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python session2_subsets_100.py session2_subsets_100.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Find two disjoint non-empty subsets S and T of the given set A of integers whose elements have the same sum."""
    A = instance["A"]  # A[i] is the i-th integer of the set
    elements = range(len(A))

    model = gp.Model("subsets_100")

    # in_S[i] is 1 when element i of A is in S, and 0 when not.
    in_S = model.addVars(elements, vtype=GRB.BINARY, name="in_S")
    # in_T[i] is 1 when element i of A is in T, and 0 when not.
    in_T = model.addVars(elements, vtype=GRB.BINARY, name="in_T")

    # The elements of S add up to the same sum as the elements of T.
    model.addConstr(gp.quicksum(A[i] * in_S[i] for i in elements)
                    == gp.quicksum(A[i] * in_T[i] for i in elements), name="equal_sums")

    # S and T are disjoint: no element is in both.
    model.addConstrs((in_S[i] + in_T[i] <= 1 for i in elements), name="disjoint")

    # S is non-empty (in_S.sum() adds in_S[i] over all elements i).
    model.addConstr(in_S.sum() >= 1, name="S_nonempty")
    # T is non-empty (in_T.sum() adds in_T[i] over all elements i).
    model.addConstr(in_T.sum() >= 1, name="T_nonempty")

    # The 0/1 outputs in_S and in_T, one entry per element of A
    return model, {"in_S": [in_S[i] for i in elements], "in_T": [in_T[i] for i in elements]}


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

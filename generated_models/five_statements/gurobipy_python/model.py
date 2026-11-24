# five_statements: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_statements.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python five_statements.py

import gurobipy as gp
from gurobipy import GRB

# N is the number of statements. The problem has no instance data: the five statements are fixed by the statement.
N = 5


def create_model(instance):
    """Five statements: statement i says that exactly i + 1 of the five statements are false. Which of them are true?"""
    model = gp.Model("five_statements")

    # statements[i] is 1 when statement i (counted from 0) is true, and 0 when it is false.
    statements = [model.addVar(vtype=GRB.BINARY, name=f"statement[{i}]") for i in range(N)]

    # false_count[k] is 1 when exactly k of the statements are false.
    false_count = model.addVars(range(N + 1), vtype=GRB.BINARY, name="false_count")
    # Exactly one count of false statements holds.
    model.addConstr(false_count.sum() == 1, name="one_count")
    # The number of false statements is N minus the number of true ones.
    model.addConstr(gp.quicksum(k * false_count[k] for k in range(N + 1))
                    == N - gp.quicksum(statements), name="count_false")

    # Statement i is true exactly when i + 1 statements are false.
    model.addConstrs((statements[i] == false_count[i + 1] for i in range(N)), name="statement_meaning")

    # There is no objective: the problem asks for a consistent assignment, so any solution answers it.
    return model, {"statements": statements}


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

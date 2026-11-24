# fibonacci_even: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python fibonacci_even.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. The constants below are not in the statement; they
# only bound the model. TERMS = 35 is enough, because f[34] = 5,702,887 is the first term
# above four million. TERM_MAX bounds each term (f[35] = 9,227,465 is the largest one
# used), and RES_MAX bounds the sum. LIMIT is the four million of the statement.
TERMS = 35
TERM_MAX = 10_000_000
LIMIT = 4_000_000
RES_MAX = 100_000_000


def create_model(instance):
    """Each term of the Fibonacci sequence is the sum of the two before it, starting from 1
    and 2. Find the sum of the even-valued terms that do not exceed four million."""
    model = gp.Model("fibonacci_even")

    # f[i] is the i-th term of the Fibonacci sequence, counting from 0, 1, 1, 2, ... (the
    # statement starts at 1, 2; the even terms are the same either way).
    f = [model.addVar(lb=0, ub=TERM_MAX, vtype=GRB.INTEGER, name=f"f[{i}]") for i in range(TERMS + 1)]
    # The first three terms, then each term is the sum of the two before it.
    model.addConstr(f[0] == 0, name="f0")
    model.addConstr(f[1] == 1, name="f1")
    model.addConstr(f[2] == 1, name="f2")
    model.addConstrs((f[i] == f[i - 1] + f[i - 2] for i in range(3, TERMS + 1)), name="fib")

    # For each term f[i] (i from 1 to TERMS), take[i] = 1 exactly when f[i] is even and below
    # four million; part[i] is then f[i], and 0 otherwise. The loop stays because each term
    # has its own parity, limit and take variables.
    total_parts = []
    for i in range(1, TERMS + 1):
        # f[i] = 2 half + odd, so odd = 1 exactly when f[i] is odd. half is not in the statement:
        # its bound is TERM_MAX / 2, which follows from f[i] <= TERM_MAX.
        half = model.addVar(lb=0, ub=TERM_MAX // 2, vtype=GRB.INTEGER, name=f"half[{i}]")
        odd = model.addVar(vtype=GRB.BINARY, name=f"odd[{i}]")
        model.addConstr(f[i] == 2 * half + odd, name=f"parity[{i}]")
        # below = 1 exactly when f[i] < four million.
        below = model.addVar(vtype=GRB.BINARY, name=f"below[{i}]")
        model.addConstr((below == 1) >> (f[i] <= LIMIT - 1), name=f"below_limit[{i}]")
        model.addConstr((below == 0) >> (f[i] >= LIMIT), name=f"at_limit[{i}]")
        # take = 1 when the term is even (odd = 0) and below four million.
        take = model.addVar(vtype=GRB.BINARY, name=f"take[{i}]")
        model.addConstr(take <= below)
        model.addConstr(take <= 1 - odd)
        model.addConstr(take >= below - odd, name=f"take[{i}]")
        # part[i] is f[i] when the term is taken and 0 otherwise. Indicator constraints are used
        # rather than a big-M, since a big-M would be 10^7 here.
        part = model.addVar(lb=0, ub=TERM_MAX, vtype=GRB.INTEGER, name=f"part[{i}]")
        model.addConstr((take == 1) >> (part == f[i]), name=f"counted[{i}]")
        model.addConstr((take == 0) >> (part == 0), name=f"skipped[{i}]")
        total_parts.append(part)

    # res is the sum of the even terms that do not exceed four million. RES_MAX is not in
    # the statement; it is only an upper bound for the sum.
    res = model.addVar(lb=0, ub=RES_MAX, vtype=GRB.INTEGER, name="res")
    model.addConstr(res == gp.quicksum(total_parts), name="sum_even_terms")

    # No objective: the sum is fixed by the constraints, so this is a satisfaction model.
    return model, {"res": res}


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

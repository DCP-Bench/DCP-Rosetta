# divisible_by_1_through_9: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python divisible_by_1_through_9.py

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. LENGTH: the number has ten digits (from the statement).
# DIGITS: each of the digits 0..9 is used exactly once (from the statement).
LENGTH = 10
DIGITS = range(10)


def create_model(instance):
    """A ten-digit number using each digit 0 to 9 exactly once, where the number formed by its
    first n digits is divisible by n for every n from 1 to 10."""
    model = gp.Model("divisible_by_1_through_9")

    # holds[i, d] is 1 when the digit at position i from the left is d.
    holds = model.addVars(LENGTH, DIGITS, vtype=GRB.BINARY, name="holds")
    # x[i] is the digit at position i from the left, read back from holds.
    x = [model.addVar(lb=0, ub=9, vtype=GRB.INTEGER, name=f"x[{i}]") for i in range(LENGTH)]
    # Each position holds exactly one digit, and x[i] is that digit.
    model.addConstrs((holds.sum(i, "*") == 1 for i in range(LENGTH)), name="one_digit")
    model.addConstrs((x[i] == gp.quicksum(d * holds[i, d] for d in DIGITS)
                      for i in range(LENGTH)), name="read")

    # Each of the digits 0 to 9 is used exactly once.
    model.addConstrs((holds.sum("*", d) == 1 for d in DIGITS), name="used_once")

    # No rule is needed against a leading 0: divisibility by 10 puts the 0 last.

    # The number formed by the first n digits is divisible by n. Written with
    # the place values 10^k the prefixes reach 10^10, where an integrality
    # tolerance of 1e-5 on one digit already moves the value by 10^4. Since
    # only the remainder matters, each place value is reduced modulo n first,
    # which keeps every coefficient below 10 and the check exact.
    for i in range(LENGTH):
        n = i + 1  # the statement's n: the first n digits must make a multiple of n
        residue = gp.quicksum((10 ** (i - j)) % n * x[j] for j in range(i + 1))
        # The reduced sum is at most 9 times the sum of its coefficients, so quotient is at most that divided by n.
        upper = sum((10 ** (i - j)) % n for j in range(i + 1)) * 9 // n
        # quotient[n] is the reduced sum divided by n: a whole number exactly when the first n digits make a multiple of n.
        quotient = model.addVar(lb=0, ub=upper, vtype=GRB.INTEGER, name=f"quotient[{n}]")
        model.addConstr(residue == n * quotient, name=f"divisible_by[{n}]")

    # No objective: any assignment satisfying the constraints is a solution.

    # The digits of the number, read from left to right.
    return model, {"digits": x}


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

# kenken: a Gurobi (Python) model from DCP Rosetta.
# Download the `kenken.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/kenken.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python kenken.py kenken.json

import gurobipy as gp
from gurobipy import GRB


def exponent(value, prime):
    """How many times prime divides value."""
    e = 0
    while value % prime == 0:
        value //= prime
        e += 1
    return e


def create_model(instance):
    """Fill an n-by-n grid with the digits 1 to n so that each digit appears once in every row
    and every column, and the digits in each cage reach the cage's result by the cage's
    operation, which is not given: +, -, x or /. Digits may repeat within a cage."""
    n = instance["n"]  # the grid is n by n, and its digits are 1 to n
    cages = instance["problem"]  # cages[k] is [result, cells] for cage k, with cells as 1-based [row, col]
    cells = range(n)  # the row and column numbers, 0 to n - 1
    values = range(1, n + 1)  # the digits, 1 to n
    # the primes up to n: the only primes that can divide a digit
    primes = [p for p in range(2, n + 1) if all(p % q for q in range(2, p))]

    model = gp.Model("kenken")

    # is_[r, c, v] is 1 when the cell in row r, column c holds digit v, and 0 when not.
    is_ = model.addVars(cells, cells, values, vtype=GRB.BINARY, name="is")
    # Each cell holds exactly one digit (is_.sum(r, c, "*") adds up over the digits).
    model.addConstrs((is_.sum(r, c, "*") == 1 for r in cells for c in cells), name="cell")
    # x[r][c] is the digit in row r, column c, read from is_.
    x = [[gp.quicksum(v * is_[r, c, v] for v in values) for c in cells] for r in cells]

    # Each row and each column contains each digit exactly once (is_.sum(r, "*", v) adds up
    # over the columns, and is_.sum("*", c, v) over the rows).
    model.addConstrs((is_.sum(r, "*", v) == 1 for v in values for r in cells), name="row")
    model.addConstrs((is_.sum("*", c, v) == 1 for v in values for c in cells), name="col")

    for k, (res, segment) in enumerate(cages):
        # the cells of cage k, 0-based
        cage = [(r - 1, c - 1) for r, c in segment]

        if len(cage) == 2:
            # Two cells a, b: a + b, a * b, a / b, b / a, a - b or b - a equals
            # the result. pair[a, b] is the joint choice of the two digits,
            # created only for the digit pairs that satisfy one of the six;
            # its marginals are the two cells' digits, which makes the pair
            # exact without a product of variables.
            (r1, c1), (r2, c2) = cage
            allowed = [
                (a, b) for a in values for b in values
                if a + b == res or a * b == res or a * res == b or b * res == a or a - b == res or b - a == res
            ]
            # pair[a, b] is the joint choice for cage k: the first cell holds a and the second holds b.
            pair = model.addVars(allowed, lb=0, ub=1, vtype=GRB.CONTINUOUS, name=f"pair[{k}]")
            # For each digit a, the pairs that start with a add up to 1 when the first cell holds a, and to 0 when not.
            model.addConstrs((gp.quicksum(pair[a, b] for (aa, b) in allowed if aa == a) == is_[r1, c1, a]
                              for a in values), name=f"first[{k}]")
            # For each digit b, the pairs that end with b add up to 1 when the second cell holds b, and to 0 when not.
            model.addConstrs((gp.quicksum(pair[a, b] for (a, bb) in allowed if bb == b) == is_[r2, c2, b]
                              for b in values), name=f"second[{k}]")
        else:
            # Any other cage: the digits sum to the result, or multiply to it.
            # use_sum is 1 for the sum and 0 for the product.
            use_sum = model.addVar(vtype=GRB.BINARY, name=f"use_sum[{k}]")
            # When the cage is a sum, its digits add up to the result.
            model.addConstr((use_sum == 1) >> (gp.quicksum(x[r][c] for r, c in cage) == res), name=f"sum[{k}]")
            # A product of digits 1..n equals the result exactly when, for every
            # prime up to n, the digits' exponents of that prime add up to the
            # result's; this states the product linearly. A result with another
            # prime factor cannot be such a product.
            rest = res
            if res >= 1:
                for p in primes:
                    rest //= p ** exponent(res, p)
            if res < 1 or rest != 1:
                # The result has a prime factor above n, so the cage cannot be a product.
                model.addConstr(use_sum == 1, name=f"no_product[{k}]")
            else:
                # When the cage is a product, the exponents of each prime add up to the result's.
                for p in primes:
                    digit_exponents = gp.quicksum(
                        exponent(v, p) * is_[r, c, v] for r, c in cage for v in values if exponent(v, p) > 0)
                    model.addConstr((use_sum == 0) >> (digit_exponents == exponent(res, p)), name=f"product[{k},{p}]")

    # No objective: any filled grid that meets the rules is a solution.

    return model, {"x": x}


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

# cmo_2012: a Gurobi (Python) model from DCP Rosetta.
# Download the `cmo_2012.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cmo_2012.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python cmo_2012.py cmo_2012.json

import gurobipy as gp
from gurobipy import GRB


def create_model(instance):
    """Given positive integers a and b with a - b prime and a * b a perfect square n * n,
    find the smallest a that is at least the given minimum."""
    min_a = instance["min_a"]  # min_a: the least a may be (the given minimum)
    # max_val: the largest value of a, b and n (not from the statement: an upper bound taken
    # from the instance data, to keep the variables finite)
    max_val = instance["max_val"]
    # bits: the binary digit positions needed for a number up to max_val (not from the statement)
    bits = range(max_val.bit_length())

    model = gp.Model("cmo_2012")
    # Tighter solver tolerances: the products below reach about max_val squared, and the
    # default tolerances could leave a visible error.
    model.Params.IntFeasTol = 1e-9
    model.Params.FeasibilityTol = 1e-9
    model.Params.NumericFocus = 3

    # a is the number being minimised
    a = model.addVar(lb=min_a, ub=max_val, vtype=GRB.INTEGER, name="a")
    # b is the second factor of a * b, a positive integer
    b = model.addVar(lb=1, ub=max_val, vtype=GRB.INTEGER, name="b")
    # n is the square root of a * b, so that a * b = n * n
    n = model.addVar(lb=0, ub=max_val, vtype=GRB.INTEGER, name="n")
    # p is the difference a - b, which must be prime
    p = model.addVar(lb=2, ub=max_val, vtype=GRB.INTEGER, name="p")

    # p is prime. Since p = a - b is below max_val, the primes below max_val are enough.
    # is_p[q] is 1 when p is the prime q (one-hot over those primes)
    primes = [q for q in range(2, max_val) if all(q % d for d in range(2, int(q ** 0.5) + 1))]
    is_p = model.addVars(primes, vtype=GRB.BINARY, name="is_p")
    model.addConstr(is_p.sum() == 1, name="one_prime")
    model.addConstr(p == gp.quicksum(q * is_p[q] for q in primes), name="p_is_prime")

    # a - b is the prime p, so a >= b and the difference is p.
    model.addConstr(a >= b, name="a_ge_b")
    model.addConstr(p == a - b, name="p_is_difference")

    # a * b = n * n. The product of two integer variables is not linear, so each product is
    # written with one factor as binary digits, x = sum of 2^k * digit[k], and then
    # x * y = sum of 2^k * part[k], where part[k] = digit[k] * y is linear because 0 <= y <= max_val.
    def binary_product(x, y, tag):
        digits = model.addVars(bits, vtype=GRB.BINARY, name=f"{tag}_bit")
        model.addConstr(x == gp.quicksum(2 ** k * digits[k] for k in bits), name=f"{tag}_binary")
        parts = model.addVars(bits, lb=0, ub=max_val, vtype=GRB.INTEGER, name=f"{tag}_part")
        for k in bits:
            # parts[k] = digits[k] * y, with 0 <= y <= max_val
            model.addConstr(parts[k] <= max_val * digits[k], name=f"{tag}_part_up[{k}]")
            model.addConstr(parts[k] <= y, name=f"{tag}_part_le_y[{k}]")
            model.addConstr(parts[k] >= y - max_val * (1 - digits[k]), name=f"{tag}_part_ge[{k}]")
        return gp.quicksum(2 ** k * parts[k] for k in bits)

    model.addConstr(binary_product(b, a, "b_times_a") == binary_product(n, n, "n_times_n"), name="product_is_square")

    # Redundant, not in the statement: n is between b and a, since a * b = n * n with b <= a.
    # Added only to narrow the search.
    model.addConstr(n <= a, name="n_le_a")
    model.addConstr(n >= b, name="n_ge_b")

    # Minimise a: the smallest a at least min_a for which such b and n exist.
    model.setObjective(a, GRB.MINIMIZE)

    return model, {"a": a, "b": b, "n": n, "p": p}


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

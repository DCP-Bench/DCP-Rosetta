# curious_set_of_integers: a Gurobi (Python) model from DCP Rosetta.
# Download the `curious_set_of_integers.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/curious_set_of_integers.html
# Then run it on the first instance (after `pip install gurobipy numpy`;
# the licence that comes with pip allows models up to 2000 variables and constraints):
#   python curious_set_of_integers.py curious_set_of_integers.json

import itertools
import math

import gurobipy as gp
from gurobipy import GRB

# The four given members belong to the problem statement, not the instance.
GIVEN = [1, 3, 8, 120]


def create_model(instance):
    """Curious set of integers: find a number that can join 1, 3, 8 and 120 so that the product of any two members of the set is one less than a perfect square."""
    n = instance["n"]              # the size of the set: the four given numbers and n - 4 new ones
    max_val = instance["max_val"]  # the largest value a new member or a square root may take; not from the statement, it bounds the search
    if n <= len(GIVEN):
        raise ValueError("the set must have at least one member beyond the given four")
    new = range(n - len(GIVEN))    # the new members (the statement asks for one)

    def square_roots(k):
        """The roots q, up to max_val, for which k * x + 1 = q * q for a whole number x in 0..max_val:
        x = (q * q - 1) // k is then a candidate for a new member, given the given number k."""
        top = min(max_val, math.isqrt(k * max_val + 1))
        return [q for q in range(1, top + 1) if (q * q - 1) % k == 0]

    model = gp.Model("curious_set_of_integers")
    # Squares of roots reach about 10^6 here, so their coefficients are that large; a tight
    # tolerance keeps the near-0 binaries exact.
    model.Params.IntFeasTol = 1e-9

    # The given numbers must have the property among themselves. A pair whose product plus one
    # is not a square with a root within max_val (or whose larger member exceeds max_val) makes
    # the model infeasible, through an empty constraint 0 >= 1.
    for a, b in itertools.combinations(GIVEN, 2):
        root = math.isqrt(a * b + 1)
        if root * root != a * b + 1 or root > max_val or b > max_val:
            model.addConstr(gp.LinExpr() >= 1, name=f"given_pair_fails[{a},{b}]")

    # For each new member x and each given number k, k * x + 1 is a square q * q.
    # pick[i, k][q] is 1 when the root for member i and number k is q.
    pick = {}
    for i in new:
        for k in GIVEN:
            pick[i, k] = model.addVars(square_roots(k), vtype=GRB.BINARY, name=f"root[{i},{k}]")
    model.addConstrs((pick[i, k].sum() == 1 for i in new for k in GIVEN), name="one_root")

    # Member x is (q * q - 1) / GIVEN[0] for its chosen root q; value[i] is that expression.
    value = [gp.quicksum((q * q - 1) // GIVEN[0] * pick[i, GIVEN[0]][q] for q in square_roots(GIVEN[0]))
             for i in new]
    # The same member comes out whichever given number's root is chosen.
    model.addConstrs((value[i] == gp.quicksum((q * q - 1) // k * pick[i, k][q] for q in square_roots(k))
                      for i in new for k in GIVEN[1:]), name="same_member")

    # A new member is none of the given numbers, so its root must not give a given number.
    model.addConstrs((pick[i, GIVEN[0]][q] == 0
                      for i in new for q in square_roots(GIVEN[0]) if (q * q - 1) // GIVEN[0] in GIVEN),
                     name="not_given")
    # Distinct new members have distinct roots, since a member is determined by its root.
    model.addConstrs((gp.quicksum(pick[i, GIVEN[0]][q] for i in new) <= 1
                      for q in square_roots(GIVEN[0])), name="distinct")

    # Two new members x and y also need x * y + 1 to be a square p * p. The product is linear
    # because y is split over x's root selection: part[q] is y when x's root is q, and 0 otherwise.
    # The root p is chosen among the roots that can occur.
    p_roots = range(1, min(max_val, math.isqrt(max_val * max_val + 1)) + 1)
    for i in new:
        for j in new:
            if j <= i:
                continue
            part = model.addVars(square_roots(GIVEN[0]), lb=0, ub=max_val, name=f"part[{i},{j}]")
            model.addConstrs((part[q] <= max_val * pick[i, GIVEN[0]][q] for q in square_roots(GIVEN[0])),
                             name=f"part_zero[{i},{j}]")
            model.addConstr(part.sum() == value[j], name=f"part_sum[{i},{j}]")
            product = gp.quicksum((q * q - 1) // GIVEN[0] * part[q] for q in square_roots(GIVEN[0]))
            p_pick = model.addVars(p_roots, vtype=GRB.BINARY, name=f"pair_root[{i},{j}]")
            model.addConstr(p_pick.sum() == 1, name=f"one_pair_root[{i},{j}]")
            model.addConstr(product + 1 == gp.quicksum(p * p * p_pick[p] for p in p_roots),
                            name=f"square_pair[{i},{j}]")

    # No objective: any choice of new members that meets the constraints is an answer.
    # The number asked for is the last new member.
    return model, {"number": value[-1]}


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

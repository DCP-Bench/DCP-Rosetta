# csplib_041_n_fractions: a Gurobi (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/csplib_041_n_fractions.html
# Run it (after `pip install gurobipy numpy`; the licence that comes with pip allows models
# up to 2000 variables and constraints) with:
#   python csplib_041_n_fractions.py

import itertools

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: nine letters, digits 1..9, as stated.
LETTERS = "ABCDEFGHI"
DIGITS = range(1, 10)


def create_model(instance):
    """Find distinct non-zero digits A to I such that A / BC + D / EF + G / HI = 1, where BC,
    EF and HI are the two-digit numbers made from B and C, E and F, and H and I."""
    model = gp.Model("n_fractions")
    # The equation multiplies up to three digits with coefficients up to 1000;
    # a tight integrality tolerance keeps a near-0 binary from leaking into it.
    model.Params.IntFeasTol = 1e-9

    # is_[L, v] is 1 when letter L is digit v, and 0 when not.
    is_ = model.addVars(LETTERS, DIGITS, vtype=GRB.BINARY, name="is")
    # digit[L] is the digit that letter L stands for, read back from is_.
    digit = {L: model.addVar(lb=1, ub=9, vtype=GRB.INTEGER, name=L) for L in LETTERS}
    # Each letter stands for exactly one digit (is_.sum(L, "*") adds up over the digits).
    for L in LETTERS:
        model.addConstr(is_.sum(L, "*") == 1, name=f"one_digit[{L}]")
        model.addConstr(digit[L] == gp.quicksum(v * is_[L, v] for v in DIGITS), name=f"read[{L}]")

    # The digits are distinct: each digit is used by at most one letter (is_.sum("*", v) adds up over the letters).
    model.addConstrs((is_.sum("*", v) <= 1 for v in DIGITS), name="distinct")

    def times(letter, expr, upper, name):
        """letter * expr for 0 <= expr <= upper, linear by disaggregating expr over
        the letter's one-hot digit: part[v] is expr when the letter is v, else 0."""
        part = model.addVars(DIGITS, lb=0, ub=upper, name=name)
        for v in DIGITS:
            model.addConstr(part[v] <= upper * is_[letter, v])
        model.addConstr(part.sum() == expr)
        return gp.quicksum(v * part[v] for v in DIGITS)

    # Not from the statement: the reference keeps each two-digit number BC, EF and HI at most 81.
    # The statement does not ask for this; it is kept so the answers do not change.
    model.addConstrs((10 * digit[tens] + digit[units] <= 81
                      for tens, units in (("B", "C"), ("E", "F"), ("H", "I"))), name="denominator")

    # Clearing denominators turns the equation into
    #   A*EF*HI + D*BC*HI + G*BC*EF == BC*EF*HI,
    # whose expansion into digits is a sum of products of three distinct
    # letters. Each such product is built as letter * (letter * letter).
    pair_cache = {}

    def pair(x, y):
        key = tuple(sorted((x, y)))
        if key not in pair_cache:
            pair_cache[key] = times(key[0], digit[key[1]], 9, f"prod[{key[0]}{key[1]}]")
        return pair_cache[key]

    def triple(x, y, z):
        return times(x, pair(y, z), 81, f"prod[{x}{y}{z}]")

    def two_digit(tens, units):
        return [(10, tens), (1, units)]

    BC, EF, HI = two_digit("B", "C"), two_digit("E", "F"), two_digit("H", "I")

    def expand(numerator, first, second):
        """numerator * first * second, where first and second are two-digit numbers."""
        return gp.quicksum(c1 * c2 * triple(numerator, d1, d2)
                           for (c1, d1), (c2, d2) in itertools.product(first, second))

    left = expand("A", EF, HI) + expand("D", BC, HI) + expand("G", BC, EF)
    right = gp.quicksum(c1 * c2 * c3 * triple(d1, d2, d3)
                        for (c1, d1), (c2, d2), (c3, d3) in itertools.product(BC, EF, HI))

    # A / BC + D / EF + G / HI = 1, with the denominators cleared.
    model.addConstr(left == right, name="fractions_sum_to_one")

    # No objective: any assignment that meets the constraints is a solution.

    return model, {L: digit[L] for L in LETTERS}


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

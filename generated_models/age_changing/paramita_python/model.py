# age_changing: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/age_changing.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python age_changing.py

from itertools import permutations

from paramita.containers import CnfFormula
from paramita.modelling import And, Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Start with my age and apply the four operations +2, /8, -3 and *7 in some
    order: the result is my husband's age. Starting with his age and applying the
    same four operations in a different order gives my age. Find our two ages."""
    ages = range(1, 151)  # ages are whole years from 1 to 150

    # The four operations. None means the operation cannot be applied to the age:
    # a division must come out whole, and no age may go below zero.
    ops = {
        "+2": lambda x: x + 2,
        "/8": lambda x: x // 8 if x % 8 == 0 else None,
        "-3": lambda x: x - 3 if x >= 3 else None,
        "*7": lambda x: x * 7,
    }

    def apply_order(order, x):
        # The age after the operations in order are applied to x, or None if one of
        # them cannot be applied.
        for op in order:
            x = ops[op](x)
            if x is None:
                return None
        return x

    # All orders of the four operations.
    orders = list(permutations(ops))
    # my[v] is true when my age is v, and hus[v] when his age is v.
    my = {v: Bool(f"my_age_{v}") for v in ages}
    hus = {v: Bool(f"husband_age_{v}") for v in ages}
    # fwd[p] is true when the operations are applied to my age in order p. bwd[p] is
    # true when they are applied to his age in order p.
    fwd = {p: Bool(f"forward_order_{i}") for i, p in enumerate(orders)}
    bwd = {p: Bool(f"backward_order_{i}") for i, p in enumerate(orders)}

    # Each age is a single whole number of years.
    constraints = [sum(my.values()) == 1, sum(hus.values()) == 1]
    # Exactly one order is applied to my age.
    constraints.append(sum(fwd.values()) == 1)
    # Exactly one order is applied to his age.
    constraints.append(sum(bwd.values()) == 1)

    for p in orders:
        # The order applied to his age differs from the order applied to my age.
        constraints.append(~(fwd[p] & bwd[p]))
        # Applying order p to my age gives his age. If order p cannot be applied to
        # my age v, then v is not my age.
        for v in ages:
            w = apply_order(p, v)
            if w is None or w not in hus:
                constraints.append(If(fwd[p], ~my[v]))
            else:
                constraints.append(If(And(fwd[p], my[v]), hus[w]))
        # Applying order p to his age gives my age. If order p cannot be applied to
        # his age v, then v is not his age.
        for v in ages:
            w = apply_order(p, v)
            if w is None or w not in my:
                constraints.append(If(bwd[p], ~hus[v]))
            else:
                constraints.append(If(And(bwd[p], hus[v]), my[w]))

    h = sum(v * hus[v] for v in ages)  # my husband's age
    m = sum(v * my[v] for v in ages)   # my age

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"h": h, "m": m}


if __name__ == "__main__":
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    (formula, pool), outputs = create_model({})

    solver = SatSolver.from_name("Cadical300")
    # copy the formula into the solver
    solver.add_clauses(formula.clauses())

    if solver.solve():
        # the value of every variable by name: a literal is true when it is positive
        truth = {pool.decode_literal(abs(lit)).name: lit > 0 for lit in solver.model()}
        value = np.vectorize(lambda e: evaluate(e, truth))  # make it work on nested variables
        for name, output in outputs.items():
            print(name, "=", value(output))
    else:
        print("No solution")

# giant_cat_army: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/giant_cat_army.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python giant_cat_army.py

from math import isqrt

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf

# The list has 24 numbers. The first is 0 and the last is 14.
LENGTH = 24
# Every number on the list is at most 60.
MAX_VALUE = 60
START, END = 0, 14
# The three ways to build the next number.
OPERATIONS = ("add5", "add7", "sqrt")


# The number that operation op gives from v, or None when that step is not allowed.
def successor(v, op):
    if op == "add5":
        w = v + 5
    elif op == "add7":
        w = v + 7
    else:
        w = isqrt(v)
        if w * w != v:  # only a whole square root is allowed
            return None
    return w if w <= MAX_VALUE else None


def create_model(instance):
    """Build a list that starts with 0. Each step adds 5, adds 7 or takes the square root,
    giving whole numbers only. The list has 24 numbers, all distinct and at most 60, ends
    with 14, and has 2 before 10."""
    values = range(MAX_VALUE + 1)

    # at[i][v] is true when position i of the list holds the number v.
    at = [{v: Bool(f"p_{i}_{v}") for v in values} for i in range(LENGTH)]
    # step[i][k] is true when the step from position i to position i + 1 uses operation k.
    step = [{k: Bool(f"op_{i}_{k}") for k in OPERATIONS} for i in range(LENGTH - 1)]

    constraints = []

    # Each position of the list holds exactly one number.
    constraints += [sum(at[i].values()) == 1 for i in range(LENGTH)]

    # The list starts with 0 and ends with 14.
    constraints.append(at[0][START])
    constraints.append(at[LENGTH - 1][END])

    # Each step uses exactly one operation.
    constraints += [sum(step[i].values()) == 1 for i in range(LENGTH - 1)]

    # The numbers on the list are distinct.
    constraints += [sum(at[i][v] for i in range(LENGTH)) <= 1 for v in values]

    # Each step takes the number before it to the next one. A step that the rules do not
    # allow from its number is ruled out.
    for i in range(LENGTH - 1):
        for v in values:
            for k in OPERATIONS:
                w = successor(v, k)
                if w is None:
                    constraints.append(~(at[i][v] & step[i][k]))
                else:
                    constraints.append(If(at[i][v] & step[i][k], at[i + 1][w]))

    # 2 and 10 each appear on the list once.
    constraints.append(sum(at[i][2] for i in range(LENGTH)) == 1)
    constraints.append(sum(at[i][10] for i in range(LENGTH)) == 1)
    # 10 comes after 2.
    for j in range(1, LENGTH):
        constraints.append(If(at[j][10], sum(at[i][2] for i in range(j)) >= 1))

    # The list, in order.
    outputs = {"x": [sum(v * at[i][v] for v in values) for i in range(LENGTH)]}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), outputs


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

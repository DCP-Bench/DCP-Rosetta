# hanging_weights: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/hanging_weights.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python hanging_weights.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

# The thirteen weights, named by letter.
LETTERS = "abcdefghijklm"
# Each weight is an integer from LO to HI.
LO, HI = 1, 13


def create_model(instance):
    """Thirteen weights A to M, each an integer from 1 to 13, hang from a system of bars.
    The weights on either side of a pivot balance when weighted by their distance from
    the pivot, and a bar hanging beneath another counts as its total weight. Find the
    weights that make the diagram balance."""
    constraints = []

    # weight[n] is the value of weight n. is_value[n][v] is true when weight n is v.
    weight = {}
    for n in LETTERS:
        is_value = {v: Bool(f"w_{n}_{v}") for v in range(LO, HI + 1)}
        # Each weight has exactly one value.
        constraints.append(sum(is_value.values()) == 1)
        weight[n] = sum(v * b for v, b in is_value.items())

    A, B, C, D, E, F, G = (weight[x] for x in "abcdefg")
    H, I, J, K, L, M = (weight[x] for x in "hijklm")

    # The total weight on each bar, including the bars hanging beneath it.
    bar_ef = E + F  # the bar holding E and F
    bar_hi = H + I + bar_ef  # the bar holding H and I, with the E-F bar beneath it
    bar_lm = bar_hi + L + M  # the bar holding L and M, with the H-I bar beneath it
    bar_ab = A + B  # the bar holding A and B
    bar_cd = C + D  # the bar holding C and D
    bar_g = G + bar_cd  # the bar holding G, with the C-D bar beneath it
    bar_jk = bar_ab + J + K + bar_g  # the bar holding J and K, with the A-B and G bars beneath it

    # The top bar balances: the L-M bar at distance 12 on the left, the J-K bar at distance 9 on the right.
    constraints.append(12 * bar_lm == 9 * bar_jk)
    # The bar holding L and M: the H-I bar at distance 3 on the left, L at distance 3 and M at distance 12 on the right.
    constraints.append(3 * bar_hi == 3 * L + 12 * M)
    # The bar holding H and I: H at distance 9 on the left, the E-F bar at distance 6 and I at distance 9 on the right.
    constraints.append(9 * H == 6 * bar_ef + 9 * I)
    # The bar holding E and F: E at distance 9 on the left, F at distance 6 on the right.
    constraints.append(9 * E == 6 * F)
    # The bar holding J and K: the A-B bar at distance 9 and J at distance 6 on the left, K at distance 3 and the G bar at distance 6 on the right.
    constraints.append(9 * bar_ab + 6 * J == 3 * K + 6 * bar_g)
    # The bar holding A and B: A at distance 12 on the left, B at distance 3 on the right.
    constraints.append(12 * A == 3 * B)
    # The bar holding G: G at distance 9 on the left, the C-D bar at distance 6 on the right.
    constraints.append(9 * G == 6 * bar_cd)
    # The bar holding C and D: C at distance 15 on the left, D at distance 3 on the right.
    constraints.append(15 * C == 3 * D)

    # The weight of each letter.
    outputs = {n: weight[n] for n in LETTERS}

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

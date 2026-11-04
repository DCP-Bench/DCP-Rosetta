# best_host: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/best_host.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python best_host.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

# The guests are numbered 0 Andrew, 1 Betty, 2 Cara, 3 Dave, 4 Erica, 5 Frank.
N = 6  # six guests and six seats around the table

# WILLING[g] is the set of guests that guest g will sit next to
WILLING = {
    0: {3, 5},  # Andrew will sit next to Dave and Frank
    1: {2, 4},  # Betty will sit next to Cara and Erica
    2: {1, 5},  # Cara will sit next to Betty and Frank
    3: {0, 4},  # Dave will sit next to Andrew and Erica
    4: {1, 3},  # Erica will sit next to Betty and Dave
    5: {0, 2},  # Frank will sit next to Andrew and Cara
}


def create_model(instance):
    """Seat six guests around a round table so that every guest sits next to
    guests they will accept. Each guest only accepts two particular neighbours."""
    # s[g][p] is true when guest g sits in seat p; the seats run around the table
    s = [[Bool(f"seat_{g}_{p}") for p in range(N)] for g in range(N)]

    constraints = []

    # Each guest sits in exactly one seat.
    for g in range(N):
        constraints.append(sum(s[g]) == 1)

    # Each seat holds exactly one guest.
    for p in range(N):
        constraints.append(sum(s[g][p] for g in range(N)) == 1)

    # Two guests who will not sit next to each other are never in neighbouring seats.
    for p in range(N):
        q = (p + 1) % N  # the seat after seat p, with seat 5 followed by seat 0
        for g in range(N):
            for h in range(N):
                if g != h and h not in WILLING[g]:
                    constraints.append(~(s[g][p] & s[h][q]))

    # The guest in each seat, in seating order.
    outputs = {"x": [sum(g * s[g][p] for g in range(N)) for p in range(N)]}

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

# session1_bank_card: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session1_bank_card.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session1_bank_card.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

POSITIONS = ["a", "b", "c", "d"]
DIGITS = range(10)


def create_model(instance):
    """A bank card has a four-digit PIN abcd: no two digits are the same, the
    two-digit number cd is 3 times ab, and da is 2 times bc."""
    # x[P][v] is true when the PIN has the digit v at position P
    x = {P: {v: Bool(f"x_{P}_{v}") for v in DIGITS} for P in POSITIONS}
    subject_to = []

    # Each position of the PIN holds exactly one digit.
    for P in POSITIONS:
        subject_to.append(sum(x[P][v] for v in DIGITS) == 1)

    # No two digits are the same, so each digit appears at most once.
    for v in DIGITS:
        subject_to.append(sum(x[P][v] for P in POSITIONS) <= 1)

    # The value of each PIN digit.
    val = {P: sum(v * x[P][v] for v in DIGITS) for P in POSITIONS}
    a, b, c, d = val["a"], val["b"], val["c"], val["d"]

    # The two-digit number cd is 3 times the two-digit number ab.
    subject_to.append(10 * c + d == 3 * (10 * a + b))

    # The two-digit number da is 2 times the two-digit number bc.
    subject_to.append(10 * d + a == 2 * (10 * b + c))

    outputs = {"a": a, "b": b, "c": c, "d": d}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in subject_to:
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

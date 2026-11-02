# send_more_money: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/send_more_money.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python send_more_money.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf

LETTERS = ["s", "e", "n", "d", "m", "o", "r", "y"]  # the letters of SEND, MORE and MONEY
DIGITS = range(10)                                 # the digits 0 to 9


def create_model(instance):
    """Cryptarithmetic puzzle: give each letter a digit from 0 to 9, with different letters
    getting different digits, so that SEND + MORE = MONEY holds and no word starts with zero."""
    # x[L][v] is true when letter L stands for digit v
    x = {L: {v: Bool(f"x_{L}_{v}") for v in DIGITS} for L in LETTERS}

    constraints = []

    # Each letter stands for exactly one digit.
    for L in LETTERS:
        constraints.append(sum(x[L][v] for v in DIGITS) == 1)

    # Different letters stand for different digits: each digit goes to at most one letter.
    for v in DIGITS:
        constraints.append(sum(x[L][v] for L in LETTERS) <= 1)

    # The first letter of SEND and of MORE is not zero.
    constraints.append(~x["s"][0])
    constraints.append(~x["m"][0])

    # val[L] is the digit that letter L stands for
    val = {L: sum(v * x[L][v] for v in DIGITS) for L in LETTERS}

    # SEND, MORE and MONEY, each read as a decimal number
    send = 1000 * val["s"] + 100 * val["e"] + 10 * val["n"] + val["d"]
    more = 1000 * val["m"] + 100 * val["o"] + 10 * val["r"] + val["e"]
    money = 10000 * val["m"] + 1000 * val["o"] + 100 * val["n"] + 10 * val["e"] + val["y"]

    # The sum of SEND and MORE is MONEY.
    constraints.append(send + more == money)

    # The digit of each letter, named by the letter
    outputs = {L.lower(): val[L] for L in ["d", "e", "m", "n", "o", "r", "s", "y"]}

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

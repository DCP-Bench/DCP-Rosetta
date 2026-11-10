# crypta: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/crypta.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python crypta.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Cryptarithmetic puzzle: each letter A to J stands for a different digit from
    0 to 9, no number starts with a zero, and the addition of the two twenty-letter
    numbers gives the third."""
    first = "BAIJJAJIIAHFCFEBBJEA"  # the first number
    second = "DHFGABCDIDBIFFAGFEJE"  # the second number
    total = "GJEGACDDHFAFJBFIHEEF"  # the sum
    leading = "BDG"  # the first letter of each of the three numbers
    letters = "ABCDEFGHIJ"
    digits = range(10)

    # stands_for[L][v] is true when letter L stands for digit v.
    stands_for = {L: [Bool(f"{L}_is_{v}") for v in digits] for L in letters}
    # The digit of each letter.
    value = {L: sum(v * stands_for[L][v] for v in range(1, 10)) for L in letters}

    # carry[k] is true when column k from the right carries 1 into the column to its left.
    carry = [Bool(f"carry_{k}") for k in range(len(total))]

    constraints = []

    # Each letter stands for exactly one digit.
    constraints += [sum(stands_for[L]) == 1 for L in letters]
    # Different letters stand for different digits.
    constraints += [sum(stands_for[L][v] for L in letters) == 1 for v in digits]
    # No number starts with zero.
    constraints += [~stands_for[L][0] for L in leading]
    # The sum has no column beyond the leftmost, so nothing is carried out of it.
    constraints.append(~carry[len(total) - 1])

    # Column by column from the right: the digits of the two numbers, plus the carry from
    # the column to the right, give the digit of the sum plus ten times the carry out.
    for k in range(len(total)):
        i = len(total) - 1 - k
        a, b, r = value[first[i]], value[second[i]], value[total[i]]
        if k == 0:
            constraints.append(a + b == r + 10 * carry[k])
        else:
            constraints.append(a + b + carry[k - 1] == r + 10 * carry[k])

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {L: value[L] for L in letters}


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

# divisible_by_1_through_9: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/divisible_by_1_through_9.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python divisible_by_1_through_9.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Find a 10-digit number that uses each digit 0 to 9 exactly once, where the
    number formed by its first n digits is divisible by n, for n = 1 to 10."""
    # The problem states the length, so the instance holds no data.
    n_digits = 10

    # y[p][v] is true when the digit at position p (read from the left, p = 1..10) is v.
    y = {p: {v: Bool(f"digit_{p}_is_{v}") for v in range(10)} for p in range(1, n_digits + 1)}
    # digit[p] is the value of the digit at position p, as an integer expression.
    digit = {p: sum(v * y[p][v] for v in range(10)) for p in range(1, n_digits + 1)}

    # Every position holds exactly one digit.
    constraints = [sum(y[p].values()) == 1 for p in range(1, n_digits + 1)]
    # The leading digit is not zero.
    constraints.append(~y[1][0])

    # Each of the digits 0 to 9 is used exactly once.
    constraints += [sum(y[p][v] for p in range(1, n_digits + 1)) == 1 for v in range(10)]

    # The number formed by the first n digits is divisible by n (n = 1 holds for any digit).
    # That number is sum(10**(n-p) * digit[p]) and only its remainder modulo n matters, so
    # each place value is replaced by its remainder modulo n. The reduced sum equals n
    # times a quotient, and the quotient is bounded by the largest value the sum can take.
    for n in range(2, n_digits + 1):
        residue = {p: pow(10, n - p, n) for p in range(1, n + 1)}
        top = sum(9 * residue[p] for p in range(1, n + 1)) // n
        # t[j] is true when the quotient is j.
        t = {j: Bool(f"prefix_{n}_quotient_is_{j}") for j in range(top + 1)}
        constraints.append(sum(t.values()) == 1)
        constraints.append(sum(residue[p] * digit[p] for p in range(1, n + 1))
                           == sum(n * j * t[j] for j in range(1, top + 1)))

    outputs = {"digits": [digit[p] for p in range(1, n_digits + 1)]}

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

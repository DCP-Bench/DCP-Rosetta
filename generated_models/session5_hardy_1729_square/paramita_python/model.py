# session5_hardy_1729_square: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/session5_hardy_1729_square.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python session5_hardy_1729_square.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Find four different numbers from 1 to 100 such that the sum of the squares of the
    first two equals the sum of the squares of the last two: a^2 + b^2 = c^2 + d^2."""
    values = range(1, 101)  # the numbers the four may be
    names = ["a", "b", "c", "d"]
    # The largest square is 100 * 100 = 10000, below 2 ** 14, so 14 bits hold every square.
    n_bits = 14

    # value[x][v] is true when number x is v
    value = {x: {v: Bool(f"{x}_is_{v}") for v in values} for x in names}
    # square_bits[x][k] is bit k of the square of number x
    square_bits = {x: [Bool(f"{x}_square_bit_{k}") for k in range(n_bits)] for x in names}

    # The square of number x, from its bits.
    def square_of(x):
        return sum(2**k * square_bits[x][k] for k in range(n_bits))

    cons = []

    # Each of a, b, c, d is one number from 1 to 100.
    for x in names:
        cons.append(sum(value[x].values()) == 1)

    # The four numbers are different: each value is taken by at most one of them.
    for v in values:
        cons.append(sum(value[x][v] for x in names) <= 1)

    # The bits of each square spell the square of the chosen number.
    for x in names:
        for v in values:
            for k in range(n_bits):
                bit = (v * v >> k) & 1
                cons.append(If(value[x][v], square_bits[x][k] if bit else ~square_bits[x][k]))

    # a^2 + b^2 = c^2 + d^2
    cons.append(square_of("a") + square_of("b") == square_of("c") + square_of("d"))

    # the four numbers a, b, c, d
    outputs = {x: sum(v * value[x][v] for v in values) for x in names}

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
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

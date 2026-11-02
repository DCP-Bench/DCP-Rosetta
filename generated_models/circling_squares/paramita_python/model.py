# circling_squares: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/circling_squares.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python circling_squares.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Place a different whole number in each of ten squares around a circle, so that two adjacent
    squares have the same sum of squares as the two squares opposite them."""
    # the squares in circle order; square i is next to i - 1 and i + 1, and opposite i + 5
    squares = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
    # whole numbers of at most two figures, no fractions
    lo, hi = 0, 99
    # bits needed for the largest square, 99 * 99
    sq_bits = (hi * hi).bit_length()
    # the numbers placed as examples in the puzzle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}

    constraints = []

    # is_num[p][v] is true when square p holds the number v
    is_num = {p: {v: Bool(f"{p}_is_{v}") for v in range(lo, hi + 1)} for p in squares}
    # value[p] is the number in square p
    value = {p: sum(v * is_num[p][v] for v in range(lo, hi + 1)) for p in squares}

    # Each square holds exactly one number.
    for p in squares:
        constraints.append(sum(is_num[p].values()) == 1)

    # Each number is in at most one square, so the ten squares hold different numbers.
    for v in range(lo, hi + 1):
        constraints.append(sum(is_num[p][v] for p in squares) <= 1)

    # The numbers given as examples stand as they are.
    for p, v in given.items():
        constraints.append(value[p] == v)

    # square[p] is the square of the number in square p, built from bits
    square = {}
    for p in squares:
        # bits[k] is bit k of square p
        bits = [Bool(f"{p}_square_bit_{k}") for k in range(sq_bits)]
        # the bits match the square of the number in square p
        for v in range(lo, hi + 1):
            for k in range(sq_bits):
                constraints.append(If(is_num[p][v], bits[k] if (v * v >> k) & 1 else ~bits[k]))
        square[p] = sum((2 ** k) * bits[k] for k in range(sq_bits))

    # Two adjacent squares have the same sum of squares as the two squares opposite them.
    # The pair i, i + 1 is compared with i + 5, i + 6; the equation for i + 5 is the same as for i,
    # so i from 0 to 4 covers all ten.
    for i in range(5):
        a, b = squares[i], squares[(i + 1) % 10]
        c, d = squares[(i + 5) % 10], squares[(i + 6) % 10]
        constraints.append(square[a] + square[b] == square[c] + square[d])

    # the numbers in the squares, reported by square name
    outputs = {p: value[p] for p in squares}

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

# pythagorean_triplet: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/pythagorean_triplet.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python pythagorean_triplet.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, add_to_container, to_cnf


def create_model(instance):
    """Find three natural numbers a < b < c with a^2 + b^2 = c^2 and a + b + c = 1000."""
    total_sum = 1000

    # Since a < b < c are natural numbers that add up to 1000, a is at most (1000 - 3) // 3,
    # b at most (1000 - 2) // 2 and c at most 1000 - 2.
    a_max = (total_sum - 3) // 3
    b_max = (total_sum - 2) // 2
    c_max = total_sum - 2

    # The squares of the numbers up to c_max are written in this many binary digits.
    square_size = (c_max * c_max).bit_length()

    def natural_number(name, largest):
        # A whole number from 1 to largest, held as statements "at least k" for k = 1 .. largest.
        # Being at least k + 1 implies being at least k.
        at_least = [Bool(f"{name}_at_least_{k + 1}") for k in range(largest)]
        order = [If(at_least[k + 1], at_least[k]) for k in range(largest - 1)]
        return at_least, order

    def total(statements):
        # The number of true statements, added in pairs so that the expression stays shallow.
        statements = list(statements)
        while len(statements) > 1:
            statements = [statements[i] + statements[i + 1] if i + 1 < len(statements) else statements[i]
                          for i in range(0, len(statements), 2)]
        return statements[0]

    def square_digits(name, at_least):
        # The binary digits of the square of the number, least significant first.
        # If the number is v, they are the binary digits of v * v.
        digits = [Bool(f"{name}_square_digit_{k}") for k in range(square_size)]
        cons = []
        for v in range(1, len(at_least) + 1):
            is_v = at_least[v - 1] & ~at_least[v] if v < len(at_least) else at_least[v - 1]
            for k in range(square_size):
                digit = ((v * v) >> k) & 1
                cons.append(If(is_v, digits[k] if digit else ~digits[k]))
        square = sum((1 << k) * digits[k] for k in range(square_size))
        return square, cons

    a_at_least, a_order = natural_number("a", a_max)
    b_at_least, b_order = natural_number("b", b_max)
    c_at_least, c_order = natural_number("c", c_max)
    cons = a_order + b_order + c_order

    # The numbers are natural numbers, so each is at least 1.
    cons += [a_at_least[0], b_at_least[0], c_at_least[0]]

    a = total(a_at_least)
    b = total(b_at_least)
    c = total(c_at_least)

    # a < b < c
    cons.append(a + 1 <= b)
    cons.append(b + 1 <= c)

    # a + b + c = 1000
    cons.append(a + b + c == total_sum)

    # a^2 + b^2 = c^2
    a_square, a_square_cons = square_digits("a", a_at_least)
    b_square, b_square_cons = square_digits("b", b_at_least)
    c_square, c_square_cons = square_digits("c", c_at_least)
    cons += a_square_cons + b_square_cons + c_square_cons
    cons.append(a_square + b_square == c_square)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in cons:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"a": a, "b": b, "c": c}


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

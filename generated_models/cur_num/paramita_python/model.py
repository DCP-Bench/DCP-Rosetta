# cur_num: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/cur_num.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python cur_num.py

from math import isqrt

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, If, Or, add_to_container, to_cnf

LIMIT = 10000  # the largest number allowed
BITS = LIMIT.bit_length()  # binary digits needed to write any number up to LIMIT


def create_model(instance):
    """The number 48 is peculiar: adding 1 to it gives a square number, and adding 1
    to its half gives a square number too. Find another number between 1 and 10000
    with this peculiarity."""
    # the peculiar number in base two, lowest place first
    bits = [Bool(f"peculiar_bit_{k}") for k in range(BITS)]
    peculiar = sum((2**k) * bits[k] for k in range(BITS))
    constraints = []  # the conditions the peculiar number must meet

    # The peculiar number is between 1 and 10000.
    constraints.append(peculiar >= 1)
    constraints.append(peculiar <= LIMIT)

    # It is not 48, the known example.
    constraints.append(Or(peculiar <= 47, peculiar >= 49))

    # Adding 1 gives a square number: a chosen root squared is peculiar + 1.
    max_root = isqrt(LIMIT + 1)  # the largest root that can occur, since 101 * 101 is above LIMIT + 1
    # root_a[a] is true when a is the chosen root
    root_a = {a: Bool(f"root_a_{a}") for a in range(1, max_root + 1)}
    constraints.append(sum(root_a.values()) == 1)
    constraints.append(sum(a * a * root_a[a] for a in root_a) == peculiar + 1)

    # The peculiar number is even, so its half is a whole number.
    constraints.append(~bits[0])
    # the peculiar number divided by two
    half = sum((2**k) * bits[k + 1] for k in range(BITS - 1))

    # Adding 1 to the half gives a square number: a chosen root squared is half + 1.
    max_half_root = isqrt(LIMIT // 2 + 1)  # the largest root that can occur, since the half is at most 5000
    # root_b[b] is true when b is the chosen root
    root_b = {b: Bool(f"half_root_{b}") for b in range(1, max_half_root + 1)}
    constraints.append(sum(root_b.values()) == 1)
    n_half_square_bits = (max_half_root * max_half_root).bit_length()  # the binary digits needed for the largest square
    # the square of the chosen root, lowest place first
    half_square_bits = [Bool(f"half_square_bit_{k}") for k in range(n_half_square_bits)]
    for b in root_b:
        square = b * b
        for k in range(n_half_square_bits):
            if (square >> k) & 1:
                constraints.append(If(root_b[b], half_square_bits[k]))
            else:
                constraints.append(If(root_b[b], ~half_square_bits[k]))
    constraints.append(sum((2**k) * half_square_bits[k] for k in range(n_half_square_bits)) == half + 1)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"peculiar": peculiar}


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

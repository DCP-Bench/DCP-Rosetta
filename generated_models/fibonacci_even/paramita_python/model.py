# fibonacci_even: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fibonacci_even.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python fibonacci_even.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, Iff, add_to_container, to_cnf


def create_model(instance):
    """Each new term in the Fibonacci sequence is the sum of the previous two.
    Starting from 1 and 2, find the sum of the even-valued terms that do not
    exceed four million."""
    n_terms = 32  # the first 32 terms include every term that does not exceed four million
    n_bits = 22   # every term used fits in 22 bits, since the largest, 3524578, is below 2**22

    # bits[i][k] is bit k of term i, where bit 0 is the lowest and counts 1
    bits = [[Bool(f"term_{i}_bit_{k}") for k in range(n_bits)] for i in range(n_terms)]

    # term(i) is the value of term i, read from its bits
    def term(i):
        return sum(2**k * bits[i][k] for k in range(n_bits))

    # The sequence starts with 1 and 2.
    constraints = [term(0) == 1, term(1) == 2]

    # Each later term is the sum of the two terms before it.
    for i in range(n_terms - 2):
        constraints.append(term(i + 2) == term(i) + term(i + 1))

    # A term is even when its lowest bit is not set. even_bits[i][k] is true when
    # term i is even and bit k of term i is set. The even terms are the sum of these bits.
    contributions = []
    for i in range(n_terms):
        for k in range(1, n_bits):
            even_bit = Bool(f"even_{i}_bit_{k}")
            constraints.append(Iff(even_bit, bits[i][k] & ~bits[i][0]))
            contributions.append(2**k * even_bit)

    # res is the sum of the even-valued terms.
    res = sum(contributions)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"res": res}


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

# five_brigands: a Paramita (Python) model from DCP Rosetta.
#   https://dcp-bench.github.io/DCP-Rosetta/problems/five_brigands.html
# Install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python five_brigands.py

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Five Spanish brigands captured exactly 200 doubloons altogether. Had
    Alfonso twelve times as much, Benito three times, Carlos the same, Diego
    half and Esteban a third, they would still have 200 doubloons altogether.
    Each brigand has at least one doubloon. How many doubloons has each?"""
    total = 200                   # the doubloons the brigands captured altogether
    n_bits = total.bit_length()   # the bits that write a count up to total

    def doubloons(name):
        # bits[k] is true when 2 ** k is counted in the doubloons of this brigand beyond the first
        bits = [Bool(f"{name}_bit_{k}") for k in range(n_bits)]
        # Every brigand has one doubloon, plus the bits that are set.
        return 1 + sum(2 ** k * b for k, b in enumerate(bits))

    # A, B, C, D and E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban
    A, B, C, D, E = (doubloons(name) for name in "ABCDE")

    # Together they have 200 doubloons.
    constraints = [A + B + C + D + E == total]
    # With the changed amounts they still have 200 doubloons. Multiplied by 6 to
    # clear the fractions: 12A + 3B + C + D/2 + E/3 = 200 becomes 72A + 18B + 6C + 3D + 2E = 1200.
    constraints.append(72 * A + 18 * B + 6 * C + 3 * D + 2 * E == 6 * total)

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"A": A, "B": B, "C": C, "D": D, "E": E}


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

# fifty_puzzle: a Paramita (Python) model from DCP Rosetta.
# Download the `fifty_puzzle.json` instances from the model's page:
#   https://dcp-bench.github.io/DCP-Rosetta/problems/fifty_puzzle.html
# Then install Paramita with its CaDiCaL solver (the build needs Linux, git, cmake
# and a C++ compiler) and run the model on the first instance:
#   pip install paramita numpy
#   paramita plugins build cmake '#sat-solvers/cadical-3.0.0'
#   python fifty_puzzle.py fifty_puzzle.json

from paramita.containers import CnfFormula
from paramita.modelling import Bool, DimacsVariablePool, add_to_container, to_cnf


def create_model(instance):
    """Dummies numbered with integers are to be knocked over with baseballs:
    choose the dummies to knock down so that their numbers add up to exactly
    the target sum, neither more nor less."""
    values = instance["values"]          # values[i]: the number on dummy i
    target_sum = instance["target_sum"]  # the sum the knocked-over numbers must reach

    # knocked[i] is true when dummy i is knocked over
    knocked = [Bool(f"knocked_{i}") for i in range(len(values))]

    # The numbers on the knocked-over dummies add up to exactly the target sum.
    constraints = [sum(v * k for v, k in zip(values, knocked)) == target_sum]

    # Encode the constraints into a formula of clauses. The pool gives each Bool its number
    # in the clauses.
    formula = CnfFormula()
    pool = DimacsVariablePool()
    for constraint in constraints:
        add_to_container(constraint, to_cnf, formula, pool)

    return (formula, pool), {"dummies": knocked}


if __name__ == "__main__":
    import json
    import sys
    import numpy as np
    from paramita.modelling import evaluate
    from paramita.solvers import SatSolver

    instances = json.load(open(sys.argv[1]))
    index = 0 if len(sys.argv) <= 2 else int(sys.argv[2])

    (formula, pool), outputs = create_model(instances[index])

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
